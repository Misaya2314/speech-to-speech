import asyncio
import json
import logging
import websockets
import threading
import argparse
from queue import Queue
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("S2SWebSocketServer")

class S2SWebSocketServer:
    """
    WebSocket服务器，处理前端UI与S2S语音处理系统之间的通信。
    作为独立的服务运行，使得前端UI和后端处理系统可以完全分离。
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
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
    
    async def handle_client(self, websocket, path):
        """处理单个客户端的WebSocket通信"""
        await self.register(websocket)
        try:
            await self.send_status(websocket, "connected", {"config": self.pipeline_config})
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type", "")
                    message_data = data.get("data", {})
                    
                    # 根据消息类型处理请求
                    if message_type == "start_listening":
                        logger.info("接收到开始监听请求")
                        await self.start_pipeline(websocket, message_data)
                    
                    elif message_type == "stop_listening":
                        logger.info("接收到停止监听请求")
                        await self.stop_pipeline(websocket)
                    
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
                        if audio_data:
                            self.audio_input_queue.put(audio_data)
                    
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
            await self.unregister(websocket)
    
    async def start_pipeline(self, websocket, config: Dict[str, Any]):
        """启动S2S语音处理管道"""
        # 更新配置
        if "language" in config:
            self.pipeline_config["language"] = config["language"]
        
        # 这里应该启动实际的S2S管道
        # 在完整实现中，这里会与s2s_pipeline.py集成
        
        await self.send_status(websocket, "pipeline_started", {
            "config": self.pipeline_config
        })
        
        # 启动发送结果的任务
        asyncio.create_task(self.send_results(websocket))
    
    async def stop_pipeline(self, websocket):
        """停止S2S语音处理管道"""
        # 在完整实现中，这里会停止S2S管道
        
        await self.send_status(websocket, "pipeline_stopped")
    
    async def send_results(self, websocket):
        """将处理结果发送到客户端"""
        while True:
            await asyncio.sleep(0.1)  # 避免CPU占用过高
            
            # 检查是否有文本结果要发送
            if not self.text_output_queue.empty():
                text = self.text_output_queue.get()
                await websocket.send(json.dumps({
                    "type": "transcription" if text.get("is_transcription") else "response",
                    "data": {
                        "text": text.get("text", ""),
                        "language": text.get("language", "en")
                    }
                }))
            
            # 检查是否有音频结果要发送
            if not self.audio_output_queue.empty():
                audio_data = self.audio_output_queue.get()
                await websocket.send(json.dumps({
                    "type": "audio_chunk",
                    "data": {
                        "audio": audio_data,
                        "is_last": audio_data.get("is_last", False)
                    }
                }))
    
    async def start_server(self):
        """启动WebSocket服务器"""
        server = await websockets.serve(
            self.handle_client, self.host, self.port
        )
        logger.info(f"WebSocket服务器已启动 - 监听 {self.host}:{self.port}")
        return server
    
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
    parser.add_argument("--port", type=int, default=8765, help="服务器端口号")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    server = S2SWebSocketServer(host=args.host, port=args.port)
    server.run() 