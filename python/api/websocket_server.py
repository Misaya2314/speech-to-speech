import asyncio
import json
import logging
import os
import sys
import websockets
import threading
import argparse
import time
import functools
import base64
from queue import Queue
from typing import Dict, Any, Optional, Callable, Awaitable

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入桥接模块
from s2s_pipeline_bridge import S2SPipelineBridge

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, "websocket_server.log"))
    ]
)
logger = logging.getLogger("S2SWebSocketServer")

# 自定义装饰器，用于捕获和处理WebSocket异常
def websocket_exception_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"{func.__name__}: WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"{func.__name__} 发生错误: {str(e)}")
    return wrapper

class S2SWebSocketServer:
    """
    WebSocket服务器，处理前端UI与S2S语音处理系统之间的通信。
    作为独立的服务运行，使得前端UI和后端处理系统可以完全分离。
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8766, model_path: Optional[str] = None):
        self.host = host
        self.port = port
        self.clients = set()
        self.audio_input_queue = Queue()   # 存储从前端接收的音频数据
        self.audio_output_queue = Queue()  # 存储要发送到前端的音频数据
        self.text_input_queue = Queue()    # 存储从前端接收的文本数据
        self.text_output_queue = Queue()   # 存储要发送到前端的文本数据
        self.stop_event = threading.Event()
        self.model_path = model_path
        
        # 初始化管道配置
        self.pipeline_config = {
            "language": "en",
            "stt_model": "openai/whisper-large-v3",
            "lm_model": "meta-llama/Llama-2-7b-chat-hf",
            "tts_model": "tts_models/multilingual/multi-dataset/xtts_v2"
        }
        
        # 如果提供了本地模型路径，使用本地模型
        if self.model_path:
            logger.info(f"使用本地模型路径: {self.model_path}")
            # 设置环境变量指示使用本地模型
            os.environ["USE_LOCAL_MODELS"] = "1"
            os.environ["LOCAL_MODEL_PATH"] = self.model_path
        
        # 创建S2S管道桥接
        self.pipeline_bridge = S2SPipelineBridge()
        
        # 创建结果监听线程
        self.result_listener_running = False
        self.result_listener_thread = None
        
    async def register(self, websocket):
        """注册新的WebSocket客户端连接"""
        self.clients.add(websocket)
        logger.info(f"客户端连接: {websocket.remote_address}，当前连接数: {len(self.clients)}")
        
    async def unregister(self, websocket):
        """注销WebSocket客户端连接"""
        self.clients.remove(websocket)
        logger.info(f"客户端断开: {websocket.remote_address}，当前连接数: {len(self.clients)}")
    
    async def send_status(self, websocket, status: str, details: Optional[Dict[str, Any]] = None):
        """发送状态信息到客户端"""
        message = {
            "type": "status",
            "data": {
                "status": status,
                "details": details or {}
            }
        }
        await websocket.send(json.dumps(message))
    
    @websocket_exception_handler
    async def handle_client(self, websocket):
        """处理单个客户端的WebSocket通信"""
        await self.register(websocket)
        try:
            await self.send_status(websocket, "connected", {"config": self.pipeline_config})
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type", "")
                    message_data = data.get("data", {})
                    
                    logger.debug(f"收到消息: {message_type}")
                    
                    # 处理不同类型的消息
                    if message_type == "ping":
                        # 心跳检测
                        await websocket.send(json.dumps({"type": "pong"}))
                    
                    elif message_type == "set_language":
                        # 设置语言
                        language = message_data.get("language", "en")
                        logger.info(f"设置语言: {language}")
                        self.pipeline_config["language"] = language
                        self.pipeline_bridge.update_config({"language": language})
                        await self.send_status(websocket, "language_set", {"language": language})
                    
                    elif message_type == "set_model":
                        # 设置模型
                        model_type = message_data.get("model_type")
                        model_name = message_data.get("model_name")
                        
                        if model_type and model_name:
                            logger.info(f"设置模型 {model_type}: {model_name}")
                            
                            if model_type == "stt":
                                self.pipeline_config["stt_model"] = model_name
                                self.pipeline_bridge.update_config({"stt_model": model_name})
                            elif model_type == "llm":
                                self.pipeline_config["lm_model"] = model_name
                                self.pipeline_bridge.update_config({"lm_model": model_name})
                            elif model_type == "tts":
                                self.pipeline_config["tts_model"] = model_name
                                self.pipeline_bridge.update_config({"tts_model": model_name})
                            
                            await self.send_status(websocket, "model_set", {
                                "model_type": model_type,
                                "model_name": model_name
                            })
                    
                    elif message_type == "start_listening":
                        # 开始监听音频
                        logger.info("收到开始监听请求")
                        
                        # 如果管道未运行，启动管道
                        if not self.pipeline_bridge.is_running():
                            if self.pipeline_bridge.start_pipeline():
                                await self.send_status(websocket, "pipeline_started")
                                
                                # 启动结果监听线程
                                if not self.result_listener_running:
                                    self.start_result_listener([websocket])
                            else:
                                await self.send_status(websocket, "error", {
                                    "message": "启动管道失败"
                                })
                                continue
                        
                        # 启用语音监听
                        self.pipeline_bridge.set_listening(True)
                        await self.send_status(websocket, "listening_started")
                    
                    elif message_type == "stop_listening":
                        # 停止监听音频
                        logger.info("收到停止监听请求")
                        
                        if self.pipeline_bridge.is_running():
                            # 禁用语音监听
                            self.pipeline_bridge.set_listening(False)
                            await self.send_status(websocket, "listening_stopped")
                        else:
                            await self.send_status(websocket, "warning", {
                                "message": "管道未运行"
                            })
                    
                    elif message_type == "audio_data":
                        # 处理音频数据
                        if self.pipeline_bridge.is_running():
                            audio_base64 = message_data.get("audio")
                            if audio_base64:
                                try:
                                    audio_data = base64.b64decode(audio_base64)
                                    self.pipeline_bridge.send_audio(audio_data)
                                except Exception as e:
                                    logger.error(f"处理音频数据失败: {str(e)}")
                                    await self.send_status(websocket, "error", {
                                        "message": f"音频处理错误: {str(e)}"
                                    })
                        else:
                            logger.warning("管道未运行，无法处理音频数据")
                    
                    elif message_type == "text_input":
                        # 处理文本输入（绕过STT直接发送到LLM）
                        if self.pipeline_bridge.is_running():
                            text = message_data.get("text", "")
                            language = message_data.get("language", self.pipeline_config["language"])
                            if text:
                                self.pipeline_bridge.send_text(text, language)
                                await self.send_status(websocket, "text_sent")
                        else:
                            if self.pipeline_bridge.start_pipeline():
                                await self.send_status(websocket, "pipeline_started")
                                
                                # 启动结果监听线程
                                if not self.result_listener_running:
                                    self.start_result_listener([websocket])
                                
                                # 发送文本
                                text = message_data.get("text", "")
                                language = message_data.get("language", self.pipeline_config["language"])
                                if text:
                                    self.pipeline_bridge.send_text(text, language)
                                    await self.send_status(websocket, "text_sent")
                            else:
                                await self.send_status(websocket, "error", {
                                    "message": "启动管道失败"
                                })
                    
                    elif message_type == "response":
                        # 接收客户端处理后的响应数据（目前未使用）
                        pass
                    
                    else:
                        # 未知消息类型
                        logger.warning(f"未知消息类型: {message_type}")
                        await self.send_status(websocket, "warning", {
                            "message": f"未知消息类型: {message_type}"
                        })
                    
                except json.JSONDecodeError:
                    logger.error("无效的JSON格式")
                    await self.send_status(websocket, "error", {
                        "message": "无效的JSON格式"
                    })
                except Exception as e:
                    logger.error(f"处理消息时出错: {str(e)}")
                    await self.send_status(websocket, "error", {
                        "message": f"处理错误: {str(e)}"
                    })
        
        finally:
            # 客户端断开连接时关闭管道
            if len(self.clients) <= 1:  # 当前客户端是最后一个
                self.stop_pipeline()
            await self.unregister(websocket)
    
    def stop_pipeline(self):
        """停止S2S管道和结果监听线程"""
        # 停止结果监听线程
        self.stop_result_listener()
        
        # 停止管道
        if self.pipeline_bridge.is_running():
            self.pipeline_bridge.stop_pipeline()
    
    def start_result_listener(self, websockets_list):
        """启动结果监听线程"""
        if self.result_listener_running:
            return
        
        self.result_listener_running = True
        self.result_listener_thread = threading.Thread(
            target=self._result_listener_task,
            args=(websockets_list,),
            daemon=True
        )
        self.result_listener_thread.start()
    
    def stop_result_listener(self):
        """停止结果监听线程"""
        self.result_listener_running = False
        if self.result_listener_thread:
            self.result_listener_thread.join(timeout=2.0)
            self.result_listener_thread = None
    
    def _result_listener_task(self, websockets_list):
        """结果监听线程的任务函数"""
        logger.info("结果监听线程已启动")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.result_listener_running:
            try:
                # 检查转录结果
                transcript = self.pipeline_bridge.get_text_output(timeout=0.1, is_transcription=True)
                if transcript:
                    language_code = "auto"
                    if isinstance(transcript, tuple) and len(transcript) > 1:
                        text, language_code = transcript
                    else:
                        text = transcript
                    
                    # 发送转录结果到所有客户端
                    message = {
                        "type": "transcription",
                        "data": {
                            "text": text,
                            "language": language_code
                        }
                    }
                    self._send_to_all_clients(message, websockets_list, loop)
                
                # 检查LLM响应
                response = self.pipeline_bridge.get_text_output(timeout=0.1)
                if response:
                    # 发送LLM响应到所有客户端
                    message = {
                        "type": "llm_response",
                        "data": {
                            "text": response
                        }
                    }
                    self._send_to_all_clients(message, websockets_list, loop)
                
                # 短暂休眠以减少CPU使用率
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"结果监听线程出错: {str(e)}")
                time.sleep(1.0)  # 错误后暂停一段时间
        
        logger.info("结果监听线程已停止")
    
    def _send_to_all_clients(self, message, websockets_list, loop):
        """向所有WebSocket客户端发送消息"""
        for websocket in websockets_list:
            if websocket.open:
                asyncio.run_coroutine_threadsafe(
                    websocket.send(json.dumps(message)),
                    loop
                )

async def main(host: str, port: int, model_path: Optional[str] = None):
    """主函数，启动WebSocket服务器"""
    logger.debug("调试模式已启用")
    
    # 创建WebSocket服务器实例
    server = S2SWebSocketServer(host=host, port=port, model_path=model_path)
    
    # 启动WebSocket服务器
    async with websockets.serve(server.handle_client, host, port):
        logger.info(f"WebSocket服务器已启动 - 监听 {host}:{port}")
        await asyncio.Future()  # 运行直到被取消

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="S2S WebSocket服务器")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="WebSocket服务器主机地址")
    parser.add_argument("--port", type=int, default=8766, help="WebSocket服务器端口")
    parser.add_argument("--model_path", type=str, default=None, help="本地模型路径")
    
    args = parser.parse_args()
    
    # 启动WebSocket服务器
    try:
        asyncio.run(main(args.host, args.port, args.model_path))
    except KeyboardInterrupt:
        logger.info("服务器已手动停止") 