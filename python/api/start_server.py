#!/usr/bin/env python
"""
S2S WebSocket服务器启动脚本
用于简化服务器的启动过程
"""

import os
import sys
import argparse
import subprocess
import time
import signal

def parse_args():
    parser = argparse.ArgumentParser(description="启动S2S WebSocket服务器")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8766, help="服务器端口号")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--no_preload", action="store_true", help="禁用模型预加载，改为按需加载")
    return parser.parse_args()

def start_server(args):
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 构建命令
    cmd = [
        sys.executable,
        os.path.join(current_dir, "websocket_server.py"),
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.debug:
        cmd.append("--debug")
    
    if args.no_preload:
        cmd.append("--no_preload")
    
    # 启动服务器进程
    print(f"启动S2S WebSocket服务器: {' '.join(cmd)}")
    process = subprocess.Popen(cmd)
    
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n正在关闭服务器...")
        process.terminate()
        process.wait(timeout=5)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 保持脚本运行
    try:
        while process.poll() is None:
            time.sleep(1)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

if __name__ == "__main__":
    args = parse_args()
    start_server(args) 