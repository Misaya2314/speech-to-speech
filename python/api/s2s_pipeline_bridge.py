import logging
import os
import sys
import threading
import time
from queue import Queue
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arguments_classes.module_arguments import ModuleArguments
from arguments_classes.vad_arguments import VADHandlerArguments
from arguments_classes.whisper_stt_arguments import WhisperSTTHandlerArguments
from arguments_classes.paraformer_stt_arguments import ParaformerSTTHandlerArguments
from arguments_classes.faster_whisper_stt_arguments import FasterWhisperSTTHandlerArguments
from arguments_classes.language_model_arguments import LanguageModelHandlerArguments
from arguments_classes.open_api_language_model_arguments import OpenApiLanguageModelHandlerArguments
from arguments_classes.mlx_language_model_arguments import MLXLanguageModelHandlerArguments
from arguments_classes.parler_tts_arguments import ParlerTTSHandlerArguments
from arguments_classes.melo_tts_arguments import MeloTTSHandlerArguments
from arguments_classes.chat_tts_arguments import ChatTTSHandlerArguments
from arguments_classes.facebookmms_tts_arguments import FacebookMMSTTSHandlerArguments
from arguments_classes.socket_receiver_arguments import SocketReceiverArguments
from arguments_classes.socket_sender_arguments import SocketSenderArguments

import s2s_pipeline
from VAD.vad_handler import VADHandler
from utils.thread_manager import ThreadManager

# 在模块顶部定义logger
logger = logging.getLogger("S2SPipelineBridge")

class S2SPipelineBridge:
    """
    与s2s_pipeline.py的桥接类，用于在WebSocket服务器中控制S2S管道
    """
    
    def __init__(self):
        # 使用模块级logger
        logger.info("初始化S2SPipelineBridge")
        
        self.thread_manager = None
        self.pipeline_running = False
        self.stop_event = threading.Event()
        self.should_listen = threading.Event()
        
        # 创建队列
        self.recv_audio_chunks_queue = Queue()
        self.send_audio_chunks_queue = Queue()
        self.spoken_prompt_queue = Queue()
        self.text_prompt_queue = Queue()
        self.lm_response_queue = Queue()
        
        # 存储从WebSocket客户端接收到的配置
        self.client_config = {}
        
        # 初始化参数
        self._init_arguments()
    
    def _init_arguments(self):
        """初始化所有参数类"""
        # 使用模块级logger
        logger.info("初始化参数")
        
        # 模块参数
        self.module_kwargs = ModuleArguments(
            mode="local",
            device="cpu",
            stt="whisper",
            llm="transformers",
            tts="parler",
            log_level="info"
        )
        
        # Socket参数
        self.socket_receiver_kwargs = SocketReceiverArguments()
        self.socket_sender_kwargs = SocketSenderArguments()
        
        # VAD参数
        self.vad_handler_kwargs = VADHandlerArguments()
        
        # STT参数
        self.whisper_stt_handler_kwargs = WhisperSTTHandlerArguments()
        self.paraformer_stt_handler_kwargs = ParaformerSTTHandlerArguments()
        self.faster_whisper_stt_handler_kwargs = FasterWhisperSTTHandlerArguments()
        
        # LLM参数
        self.language_model_handler_kwargs = LanguageModelHandlerArguments()
        self.open_api_language_model_handler_kwargs = OpenApiLanguageModelHandlerArguments()
        self.mlx_language_model_handler_kwargs = MLXLanguageModelHandlerArguments()
        
        # TTS参数
        self.parler_tts_handler_kwargs = ParlerTTSHandlerArguments()
        self.melo_tts_handler_kwargs = MeloTTSHandlerArguments()
        self.chat_tts_handler_kwargs = ChatTTSHandlerArguments()
        self.facebook_mms_tts_handler_kwargs = FacebookMMSTTSHandlerArguments()
    
    def update_config(self, client_config: Dict[str, Any]):
        """根据WebSocket客户端配置更新管道配置"""
        # 使用模块级logger
        logger.info(f"更新配置: {client_config}")
        
        self.client_config.update(client_config)
        
        # 更新语言设置
        language = client_config.get("language")
        if language:
            if hasattr(self.whisper_stt_handler_kwargs, "language"):
                self.whisper_stt_handler_kwargs.language = language
            if hasattr(self.faster_whisper_stt_handler_kwargs, "language"):
                self.faster_whisper_stt_handler_kwargs.language = language
        
        # 更新STT模型
        stt_model = client_config.get("stt_model")
        if stt_model:
            if "whisper" in stt_model.lower():
                self.module_kwargs.stt = "whisper"
                if hasattr(self.whisper_stt_handler_kwargs, "model_name"):
                    # 确保Whisper模型名称格式正确
                    if stt_model == "whisper-large-v3":
                        stt_model = "openai/whisper-large-v3"
                    # 确保distil-whisper模型名称格式正确
                    elif stt_model == "distil-large-v3":
                        stt_model = "distil-whisper/distil-large-v3"
                    self.whisper_stt_handler_kwargs.stt_model_name = stt_model
                    
                    # 解决forced_decoder_ids与task冲突问题
                    # 移除默认的forced_decoder_ids设置，由模型自行处理
                    if not hasattr(self.whisper_stt_handler_kwargs, "stt_gen_forced_decoder_ids"):
                        setattr(self.whisper_stt_handler_kwargs, "stt_gen_forced_decoder_ids", None)
            elif "paraformer" in stt_model.lower():
                self.module_kwargs.stt = "paraformer"
        
        # 更新LLM模型
        lm_model = client_config.get("lm_model")
        if lm_model:
            if "openai" in lm_model.lower() or "gpt" in lm_model.lower():
                self.module_kwargs.llm = "open_api"
                if hasattr(self.open_api_language_model_handler_kwargs, "model_name"):
                    self.open_api_language_model_handler_kwargs.model_name = lm_model
            else:
                self.module_kwargs.llm = "transformers"
                if hasattr(self.language_model_handler_kwargs, "model_name"):
                    self.language_model_handler_kwargs.model_name = lm_model
        
        # 更新TTS模型
        tts_model = client_config.get("tts_model")
        if tts_model:
            if "melo" in tts_model.lower():
                self.module_kwargs.tts = "melo"
            elif "parler" in tts_model.lower():
                self.module_kwargs.tts = "parler"
            elif "chat" in tts_model.lower():
                self.module_kwargs.tts = "chatTTS"
            elif "facebook" in tts_model.lower() or "mms" in tts_model.lower():
                self.module_kwargs.tts = "facebookMMS"
    
    def start_pipeline(self):
        """启动S2S管道"""
        # 使用模块级logger
        logger.info("正在启动S2S管道...")
        
        if self.pipeline_running:
            logger.warning("S2S管道已经在运行中")
            return False
        
        try:            
            # 准备参数
            s2s_pipeline.prepare_all_args(
                self.module_kwargs,
                self.whisper_stt_handler_kwargs,
                self.paraformer_stt_handler_kwargs,
                self.faster_whisper_stt_handler_kwargs,
                self.language_model_handler_kwargs,
                self.open_api_language_model_handler_kwargs,
                self.mlx_language_model_handler_kwargs,
                self.parler_tts_handler_kwargs,
                self.melo_tts_handler_kwargs,
                self.chat_tts_handler_kwargs,
                self.facebook_mms_tts_handler_kwargs,
            )
            
            # 重置事件和队列
            self.stop_event.clear()
            self.should_listen.set()  # 默认启动监听
            
            queues_and_events = {
                "stop_event": self.stop_event,
                "should_listen": self.should_listen,
                "recv_audio_chunks_queue": self.recv_audio_chunks_queue,
                "send_audio_chunks_queue": self.send_audio_chunks_queue,
                "spoken_prompt_queue": self.spoken_prompt_queue,
                "text_prompt_queue": self.text_prompt_queue,
                "lm_response_queue": self.lm_response_queue,
            }
            
            # 构建管道
            self.thread_manager = s2s_pipeline.build_pipeline(
                self.module_kwargs,
                self.socket_receiver_kwargs,
                self.socket_sender_kwargs,
                self.vad_handler_kwargs,
                self.whisper_stt_handler_kwargs,
                self.faster_whisper_stt_handler_kwargs,
                self.paraformer_stt_handler_kwargs,
                self.language_model_handler_kwargs,
                self.open_api_language_model_handler_kwargs,
                self.mlx_language_model_handler_kwargs,
                self.parler_tts_handler_kwargs,
                self.melo_tts_handler_kwargs,
                self.chat_tts_handler_kwargs,
                self.facebook_mms_tts_handler_kwargs,
                queues_and_events,
            )
            
            # 启动管道
            self.thread_manager.start()
            self.pipeline_running = True
            logger.info("S2S管道启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动S2S管道失败: {str(e)}")
            self.stop_pipeline()
            return False
    
    def stop_pipeline(self):
        """停止S2S管道"""
        # 使用模块级logger
        if not self.pipeline_running:
            logger.warning("S2S管道未运行")
            return
        
        try:
            logger.info("正在停止S2S管道...")
            
            # 发送停止事件
            self.stop_event.set()
            
            # 停止线程管理器
            if self.thread_manager:
                self.thread_manager.stop()
                self.thread_manager = None
            
            self.pipeline_running = False
            logger.info("S2S管道已停止")
            
        except Exception as e:
            logger.error(f"停止S2S管道时出错: {str(e)}")
    
    def send_audio(self, audio_data):
        """发送音频数据到输入队列"""
        # 使用模块级logger
        if not self.pipeline_running:
            logger.warning("S2S管道未运行，无法发送音频数据")
            return False
        
        try:
            # 这里可能需要对音频数据进行解码和转换
            self.recv_audio_chunks_queue.put(audio_data)
            return True
        except Exception as e:
            logger.error(f"发送音频数据失败: {str(e)}")
            return False
    
    def send_text(self, text, language="en"):
        """直接发送文本到LLM，绕过STT阶段"""
        # 使用模块级logger
        if not self.pipeline_running:
            logger.warning("S2S管道未运行，无法发送文本")
            return False
        
        try:
            # 将文本直接放入text_prompt_queue队列
            self.text_prompt_queue.put({
                "text": text,
                "language": language
            })
            return True
        except Exception as e:
            logger.error(f"发送文本失败: {str(e)}")
            return False
    
    def set_listening(self, should_listen):
        """设置是否监听音频输入"""
        # 使用模块级logger
        if should_listen:
            self.should_listen.set()
            logger.info("已启用音频监听")
        else:
            self.should_listen.clear()
            logger.info("已禁用音频监听")
    
    def get_audio_output(self, timeout=0.1):
        """获取音频输出队列中的数据"""
        try:
            return self.send_audio_chunks_queue.get(block=True, timeout=timeout)
        except:
            return None
    
    def get_text_output(self, timeout=0.1, is_transcription=False):
        """获取文本输出队列中的数据"""
        try:
            queue = self.text_prompt_queue if is_transcription else self.lm_response_queue
            return queue.get(block=True, timeout=timeout)
        except:
            return None
    
    def is_running(self):
        """检查管道是否正在运行"""
        return self.pipeline_running 