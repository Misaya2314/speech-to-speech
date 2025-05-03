from huggingface_hub import snapshot_download
import os
import argparse

def download_model(model_id, local_dir=None, revision=None):
    """
    下载Hugging Face模型到本地目录
    
    参数:
        model_id: Hugging Face上的模型ID，如'openai/whisper-large-v3'
        local_dir: 本地保存目录，如果为None则使用默认缓存目录
        revision: 模型分支或标签，如'main'
    """
    print(f"下载模型: {model_id}")
    
    try:
        # 使用snapshot_download确保完整下载模型文件
        cache_dir = snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            revision=revision,
            local_dir_use_symlinks=False  # 不使用符号链接，复制完整文件
        )
        
        print(f"模型已成功下载到: {cache_dir}")
        return cache_dir
    except Exception as e:
        print(f"下载模型时出错: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='下载Hugging Face模型到本地')
    parser.add_argument('--model', type=str, default='openai/whisper-large-v3', help='要下载的模型ID')
    parser.add_argument('--dir', type=str, default=None, help='本地保存目录')
    parser.add_argument('--revision', type=str, default=None, help='模型分支或标签')
    
    args = parser.parse_args()
    
    # 如果没有指定目录，使用默认的本地目录
    if args.dir is None:
        args.dir = os.path.join(os.getcwd(), "models", args.model.replace("/", "_"))
        os.makedirs(args.dir, exist_ok=True)
    
    download_model(args.model, args.dir, args.revision)

if __name__ == "__main__":
    main() 