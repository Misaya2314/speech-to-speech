import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='使用本地模型运行Speech-to-Speech')
    parser.add_argument('--model_dir', type=str, default='./models', help='模型所在的本地目录')
    parser.add_argument('--no_preload', action='store_true', help='禁用模型预加载，改为按需加载')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='WebSocket服务器主机地址')
    parser.add_argument('--port', type=int, default=8766, help='WebSocket服务器端口')
    
    args = parser.parse_args()
    
    # 设置环境变量，指定本地模型目录
    os.environ['TRANSFORMERS_OFFLINE'] = '1'  # 强制离线模式
    os.environ['HF_DATASETS_OFFLINE'] = '1'   # 数据集也离线
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'  # 禁用符号链接警告
    
    # 确保使用不含中文字符的缓存路径
    os.environ['TORCH_HOME'] = os.path.abspath('models/torch_cache')
    os.environ['TRANSFORMERS_CACHE'] = os.path.abspath('models/transformers_cache')
    os.environ['HF_HOME'] = os.path.abspath('models/hf_home')
    
    # 确保目录存在
    for path in [os.environ['TORCH_HOME'], os.environ['TRANSFORMERS_CACHE'], os.environ['HF_HOME']]:
        os.makedirs(path, exist_ok=True)
    
    # 打印环境变量
    print("已设置以下环境变量:")
    print(f"TORCH_HOME = {os.environ['TORCH_HOME']}")
    print(f"TRANSFORMERS_CACHE = {os.environ['TRANSFORMERS_CACHE']}")
    print(f"HF_HOME = {os.environ['HF_HOME']}")
    print(f"TRANSFORMERS_OFFLINE = {os.environ['TRANSFORMERS_OFFLINE']}")
    
    # 指定本地模型参数
    stt_model_path = os.path.join(args.model_dir, "openai_whisper-large-v3")
    
    # 检查模型路径是否存在
    if not os.path.exists(stt_model_path):
        print(f"错误: 模型路径不存在: {stt_model_path}")
        print("请先运行 python download_models.py 下载模型")
        return 1
    
    # 准备命令行参数
    cmd = [
        sys.executable,
        "python/api/websocket_server.py",
        "--model_path", stt_model_path,
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    # 添加预加载选项
    if args.no_preload:
        cmd.append("--no_preload")
    else:
        print("模型将在服务器启动时预加载，这可能需要一些时间...")
    
    # 运行WebSocket服务器
    print(f"使用本地模型路径: {stt_model_path}")
    print(f"启动WebSocket服务器 {args.host}:{args.port}...")
    
    # 使用子进程运行服务器
    try:
        subprocess.run(cmd)
        return 0
    except Exception as e:
        print(f"运行服务器时出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 