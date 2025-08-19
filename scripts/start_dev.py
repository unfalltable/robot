#!/usr/bin/env python3
"""
开发环境启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """检查环境要求"""
    print("检查环境要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 11):
        print("错误: 需要Python 3.11或更高版本")
        return False
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("警告: 建议在虚拟环境中运行")
    
    return True

def setup_environment():
    """设置环境"""
    print("设置环境...")
    
    # 创建.env文件（如果不存在）
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("创建.env文件...")
        env_file.write_text(env_example.read_text())
    
    # 创建日志目录
    log_dir = Path("backend/logs")
    log_dir.mkdir(exist_ok=True)
    
    return True

def install_dependencies():
    """安装依赖"""
    print("安装后端依赖...")
    
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        os.chdir("..")
    
    print("安装前端依赖...")
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
    
    return True

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
        # 启动FastAPI服务
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        os.chdir("..")
        return process
    
    return None

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        # 启动Next.js服务
        process = subprocess.Popen(["npm", "run", "dev"])
        os.chdir("..")
        return process
    
    return None

def main():
    """主函数"""
    print("=== 数字货币交易机器人开发环境启动 ===")
    
    try:
        # 检查环境
        if not check_requirements():
            return 1
        
        # 设置环境
        if not setup_environment():
            return 1
        
        # 安装依赖
        install_dependencies()
        
        # 启动服务
        backend_process = start_backend()
        time.sleep(3)  # 等待后端启动
        
        frontend_process = start_frontend()
        
        print("\n=== 服务启动完成 ===")
        print("后端API: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("前端界面: http://localhost:3000")
        print("\n按 Ctrl+C 停止服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止服务...")
            
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            
            print("服务已停止")
            return 0
    
    except Exception as e:
        print(f"启动失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
