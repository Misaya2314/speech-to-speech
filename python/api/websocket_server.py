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
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8766):
        self.host = host
        self.port = port
        self.clients = set()
        self.audio_input_queue = Queue()   # 存储从前端接收的音频数据
        self.audio_output_queue = Queue()  # 存储要发送到前端的音频数据
        self.text_input_queue = Queue()    # 存储从前端接收的文本数据
        self.text_output_queue = Queue()   # 存储要发送到前端的文本数据
        self.stop_event = threading.Event()
        
        # 初始化管道配置
        self.pipeline_config = {
            "language": "en",
            "stt_model": "whisper-large-v3",
            "lm_model": "meta-llama/Llama-2-7b-chat-hf",
            "tts_model": "tts_models/multilingual/multi-dataset/xtts_v2"
        }
        
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
                    
                    # 根据消息类型处理请求
                    if message_type == "start_listening":
                        logger.info("接收到开始监听请求")
                        await self.start_pipeline(websocket, message_data)
                    
                    elif message_type == "stop_listening":
                        logger.info("接收到停止监听请求")
                        await self.stop_pipeline(websocket)
                    
                    elif message_type == "ping":
                        # 处理心跳检测
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "data": { "timestamp": int(time.time() * 1000) }
                        }))
                    
                    elif message_type == "set_language":
                        language = message_data.get("language", "en")
                        logger.info(f"设置语言: {language}")
                        self.pipeline_config["language"] = language
                        await self.send_status(websocket, "language_set", {"language": language})
                    
                    elif message_type == "set_model":
                        model_type = message_data.get("model_type", "")
                        model_name = message_data.get("model_name", "")
                        
                        if model_type and model_name:
                            logger.info(f"设置模型 {model_type}: {model_name}")
                            if model_type == "stt":
                                self.pipeline_config["stt_model"] = model_name
                            elif model_type == "lm":
                                self.pipeline_config["lm_model"] = model_name
                            elif model_type == "tts":
                                self.pipeline_config["tts_model"] = model_name
                            
                            await self.send_status(websocket, "model_set", {
                                "model_type": model_type,
                                "model_name": model_name
                            })
                    
                    elif message_type == "audio_data":
                        # 处理前端发送的音频数据
                        audio_data = message_data.get("audio")
                        if audio_data and self.pipeline_bridge.is_running():
                            # 将Base64编码的音频数据解码为字节
                            try:
                                audio_bytes = base64.b64decode(audio_data)
                                self.pipeline_bridge.send_audio(audio_bytes)
                            except Exception as e:
                                logger.error(f"处理音频数据失败: {str(e)}")
                    
                    elif message_type == "response":
                        # 处理前端发送的文本命令
                        text = message_data.get("text", "")
                        language = message_data.get("language", "en")
                        
                        if text and self.pipeline_bridge.is_running():
                            logger.info(f"接收到文本命令: {text}")
                            self.pipeline_bridge.send_text(text, language)
                    
                    else:
                        logger.warning(f"未知消息类型: {message_type}")
                        await self.send_status(websocket, "error", {
                            "message": f"未知消息类型: {message_type}"
                        })
                
                except json.JSONDecodeError:
                    logger.error("JSON解析错误")
                    await self.send_status(websocket, "error", {
                        "message": "无效的JSON格式"
                    })
                
                except Exception as e:
                    logger.error(f"处理消息时出错: {str(e)}")
                    await self.send_status(websocket, "error", {
                        "message": f"处理请求时出错: {str(e)}"
                    })
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("客户端连接关闭")
        
        finally:
            # 如果当前客户端是最后一个客户端，则停止管道
            if len(self.clients) <= 1:
                self.stop_result_listener()
                self.pipeline_bridge.stop_pipeline()
            
            await self.unregister(websocket)
    
    async def start_pipeline(self, websocket, config: Dict[str, Any]):
        """启动S2S语音处理管道"""
        # 更新配置
        if "language" in config:
            self.pipeline_config["language"] = config["language"]
        
        # 更新S2S管道配置
        self.pipeline_bridge.update_config(self.pipeline_config)
        
        # 启动S2S管道
        if self.pipeline_bridge.start_pipeline():
            # 开始监听结果
            self.start_result_listener(websocket)
            
            await self.send_status(websocket, "pipeline_started", {
                "config": self.pipeline_config
            })
        else:
            await self.send_status(websocket, "error", {
                "message": "启动S2S管道失败"
            })
    
    async def stop_pipeline(self, websocket):
        """停止S2S语音处理管道"""
        # 停止结果监听器
        self.stop_result_listener()
        
        # 停止S2S管道
        self.pipeline_bridge.stop_pipeline()
        
        await self.send_status(websocket, "pipeline_stopped")
    
    def start_result_listener(self, websocket):
        """启动结果监听线程"""
        if self.result_listener_running:
            return
        
        self.result_listener_running = True
        self.result_listener_thread = threading.Thread(
            target=self._result_listener_task,
            args=(websocket,),
            daemon=True
        )
        self.result_listener_thread.start()
        logger.info("结果监听线程已启动")
    
    def stop_result_listener(self):
        """停止结果监听线程"""
        self.result_listener_running = False
        if self.result_listener_thread:
            self.result_listener_thread.join(timeout=1.0)
            self.result_listener_thread = None
            logger.info("结果监听线程已停止")
    
    def _result_listener_task(self, websocket):
        """结果监听线程的任务函数"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.result_listener_running:
                # 检查是否有文本输出
                text_output = self.pipeline_bridge.get_text_output(timeout=0.1, is_transcription=False)
                if text_output:
                    asyncio.run_coroutine_threadsafe(
                        self._send_response(websocket, text_output),
                        loop
                    )
                
                # 检查是否有转录输出
                transcription = self.pipeline_bridge.get_text_output(timeout=0.1, is_transcription=True)
                if transcription:
                    asyncio.run_coroutine_threadsafe(
                        self._send_transcription(websocket, transcription),
                        loop
                    )
                
                # 检查是否有音频输出
                audio_output = self.pipeline_bridge.get_audio_output(timeout=0.1)
                if audio_output:
                    asyncio.run_coroutine_threadsafe(
                        self._send_audio_chunk(websocket, audio_output),
                        loop
                    )
                
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.01)
        
        except Exception as e:
            logger.error(f"结果监听线程出错: {str(e)}")
        finally:
            loop.close()
    
    async def _send_response(self, websocket, response):
        """发送LLM响应到客户端"""
        try:
            if not websocket.closed:
                await websocket.send(json.dumps({
                    "type": "response",
                    "data": {
                        "text": response.get("text", ""),
                        "language": response.get("language", "en")
                    }
                }))
        except Exception as e:
            logger.error(f"发送响应失败: {str(e)}")
    
    async def _send_transcription(self, websocket, transcription):
        """发送语音转录结果到客户端"""
        try:
            if not websocket.closed:
                await websocket.send(json.dumps({
                    "type": "transcription",
                    "data": {
                        "text": transcription.get("text", ""),
                        "language": transcription.get("language", "en")
                    }
                }))
        except Exception as e:
            logger.error(f"发送转录结果失败: {str(e)}")
    
    async def _send_audio_chunk(self, websocket, audio_chunk):
        """发送音频块到客户端"""
        try:
            if not websocket.closed:
                # 将音频数据编码为Base64字符串
                audio_base64 = base64.b64encode(audio_chunk).decode('utf-8')
                
                await websocket.send(json.dumps({
                    "type": "audio_chunk",
                    "data": {
                        "audio": audio_base64,
                        "is_last": False  # 这里可能需要根据实际情况设置
                    }
                }))
        except Exception as e:
            logger.error(f"发送音频块失败: {str(e)}")
    
    @websocket_exception_handler
    async def send_results(self, websocket):
        """将处理结果发送到客户端"""
        pass  # 这个方法已被_result_listener_task替代
    
    async def start_server(self):
        """启动WebSocket服务器"""
        port = self.port
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            try:
                server = await websockets.serve(
                    self.handle_client, self.host, port
                )
                logger.info(f"WebSocket服务器已启动 - 监听 {self.host}:{port}")
                self.port = port  # 更新实际使用的端口
                return server
            except OSError as e:
                attempt += 1
                logger.warning(f"端口 {port} 被占用，尝试使用端口 {port + 1}")
                port += 1
                
                if attempt >= max_attempts:
                    logger.error(f"尝试了 {max_attempts} 个端口后仍无法启动服务器")
                    raise e
    
    def run(self):
        """运行WebSocket服务器（阻塞）"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        server = loop.run_until_complete(self.start_server())
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在关闭服务器...")
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
            logger.info("服务器已关闭")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="S2S WebSocket Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8766, help="服务器端口号")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # 如果开启调试模式，设置日志级别为DEBUG
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    server = S2SWebSocketServer(host=args.host, port=args.port)
    server.run() 