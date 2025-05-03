from threading import Thread
from time import perf_counter
from baseHandler import BaseHandler
import numpy as np
import torch
from transformers import (
    AutoTokenizer,
)
from parler_tts import ParlerTTSForConditionalGeneration, ParlerTTSStreamer
import librosa
import logging
from rich.console import Console
from utils.utils import next_power_of_2
from transformers.utils.import_utils import (
    is_flash_attn_2_available,
)

torch._inductor.config.fx_graph_cache = True
# mind about this parameter ! should be >= 2 * number of padded prompt sizes for TTS
torch._dynamo.config.cache_size_limit = 15

# 在模块顶部定义logger，但在各方法中使用局部日志对象
logger = logging.getLogger(__name__)

console = Console()


if not is_flash_attn_2_available() and torch.cuda.is_available():
    # 使用局部日志对象
    log = logging.getLogger(__name__)
    log.warning(
        """Parler TTS works best with flash attention 2, but is not installed
        Given that CUDA is available in this system, you can install flash attention 2 with `uv pip install flash-attn --no-build-isolation`"""
    )


WHISPER_LANGUAGE_TO_PARLER_SPEAKER = {
    "en": "Jason",
    "fr": "Christine",
    "es": "Steven",
    "de": "Nicole",
    "pt": "Sophia",
    "pl": "Alex",
    "it": "Richard",
    "nl": "Mark",
}


class ParlerTTSHandler(BaseHandler):
    def setup(
        self,
        should_listen,
        device="cuda",
        torch_dtype="float16",
        compile_mode=None,
        speaker="Jason",
        max_prompt_pad_length=8,
        play_steps=10,
        chunk_size=512,
        stream=True,
        gen_kwargs={},
        **kwargs,  # 添加**kwargs以接收并忽略额外的参数，如description
    ):
        # 使用局部日志对象
        log = logging.getLogger(__name__)
        
        self.play_steps = play_steps
        self.should_listen = should_listen
        self.device = device
        self.torch_dtype = getattr(torch, torch_dtype)
        self.compile_mode = compile_mode
        self.speaker = speaker
        self.stream = stream
        self.blocksize = chunk_size
        self.max_prompt_pad_length = max_prompt_pad_length

        self.tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini")
        self.prompt_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")

        self.model = ParlerTTSForConditionalGeneration.from_pretrained(
            "parler-tts/parler-mini-v1-jenny",
            torch_dtype=self.torch_dtype,
        ).to(device)

        # compile
        if self.compile_mode:
            self.model.forward = torch.compile(
                self.model.forward, mode=self.compile_mode, fullgraph=True
            )
        self.warmup()

    def prepare_model_inputs(self, text, max_length_prompt=None, pad=False):
        input_ids = self.tokenizer(
            text,
            return_tensors="pt",
        ).input_ids.to(self.device)

        prompt_ids = self.prompt_tokenizer(
            text,
            return_tensors="pt",
        ).input_ids.to(self.device)
        if pad and max_length_prompt is not None:
            # TODO: pad to max_length_prompt
            padded_prompt_ids = torch.zeros(
                (1, max_length_prompt), dtype=torch.long, device=self.device
            )
            padded_prompt_ids[0, : prompt_ids.shape[1]] = prompt_ids
            prompt_ids = padded_prompt_ids

        # pad attention_mask
        padded_attention_mask = torch.zeros(
            (1, 1024), dtype=torch.long, device=self.device
        )
        padded_attention_mask[0, : input_ids.shape[1]] = 1
        
        result_dict = {
            "input_ids": input_ids,
            "prompt_ids": prompt_ids,
            "attention_mask": padded_attention_mask,
            "speaker": self.speaker
        }
        
        return result_dict

    def warmup(self):
        # 使用局部日志对象
        log = logging.getLogger(__name__)
        
        logger.info(f"Warming up {self.__class__.__name__}")

        if self.device == "cuda":
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)

        # 2 warmup steps for no compile or compile mode with CUDA graphs capture
        n_steps = 1 if self.compile_mode == "default" else 2

        if self.device == "cuda":
            torch.cuda.synchronize()
            start_event.record()
        if self.compile_mode:
            pad_lengths = [2**i for i in range(2, self.max_prompt_pad_length)]
            for pad_length in pad_lengths[::-1]:
                model_kwargs = self.prepare_model_inputs(
                    "dummy prompt", max_length_prompt=pad_length, pad=True
                )
                for _ in range(n_steps):
                    _ = self.model.generate(**model_kwargs)
                log.info(f"Warmed up length {pad_length} tokens!")
        else:
            model_kwargs = self.prepare_model_inputs("dummy prompt")
            for _ in range(n_steps):
                _ = self.model.generate(**model_kwargs)

        if self.device == "cuda":
            end_event.record()
            torch.cuda.synchronize()
            log.info(
                f"{self.__class__.__name__}:  warmed up! time: {start_event.elapsed_time(end_event) * 1e-3:.3f} s"
            )

    def process(self, llm_sentence):
        # 使用局部日志对象
        log = logging.getLogger(__name__)
        
        if isinstance(llm_sentence, tuple):
            llm_sentence, language_code = llm_sentence
            self.speaker = WHISPER_LANGUAGE_TO_PARLER_SPEAKER.get(language_code, "Jason")
            
        console.print(f"[green]ASSISTANT: {llm_sentence}")
        nb_tokens = len(self.prompt_tokenizer(llm_sentence).input_ids)

        pad_args = {}
        if self.compile_mode:
            # pad to closest upper power of two
            pad_length = next_power_of_2(nb_tokens)
            log.debug(f"padding to {pad_length}")
            pad_args["pad"] = True
            pad_args["max_length_prompt"] = pad_length

        tts_gen_kwargs = self.prepare_model_inputs(
            llm_sentence,
            **pad_args,
        )

        streamer = ParlerTTSStreamer(
            self.model, device=self.device, play_steps=self.play_steps
        )
        tts_gen_kwargs = {"streamer": streamer, **tts_gen_kwargs}
        torch.manual_seed(0)
        thread = Thread(target=self.model.generate, kwargs=tts_gen_kwargs)
        thread.start()

        for i, audio_chunk in enumerate(streamer):
            global pipeline_start
            if i == 0 and "pipeline_start" in globals():
                log.info(
                    f"Time to first audio: {perf_counter() - pipeline_start:.3f}"
                )
            audio_chunk = librosa.resample(audio_chunk, orig_sr=44100, target_sr=16000)
            audio_chunk = (audio_chunk * 32768).astype(np.int16)
            for i in range(0, len(audio_chunk), self.blocksize):
                yield np.pad(
                    audio_chunk[i : i + self.blocksize],
                    (0, self.blocksize - len(audio_chunk[i : i + self.blocksize])),
                )

        self.should_listen.set()
