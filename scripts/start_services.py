"""
一键启动 AI 引擎和后端服务
用于验证导学步骤+3D几何数据通道
"""
import subprocess
import sys
import time
from pathlib import Path

def start_service(name, command, cwd):
    """启动服务"""
    print(f"\n🚀 正在启动 {name}...")
    print(f"   命令: {command}")
    print(f"   目录: {cwd}")
    
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return process

def main():
    # 将 workspace_root 设为项目根目录（scripts 的上一级）
    workspace_root = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("🎯 数到渠成 - AI 导学系统启动")
    print("=" * 60)
    
    # 启动 AI 引擎服务 (端口 8001)
    ai_engine_dir = workspace_root / "ai_engine"
    ai_process = start_service(
        "AI 引擎服务",
        f"{sys.executable} main.py",
        ai_engine_dir
    )
    
    time.sleep(2)
    
    # 启动后端服务 (端口 8000)
    # 注意这里使用 backend_service 目录下的 main.py 中的 app，
    # 该 app 已经 include_router(api.routes)，包含 /api/capture/text 等所有业务路由。
    backend_dir = workspace_root / "backend_service"
    backend_process = start_service(
        "后端服务",
        f"{sys.executable} -m uvicorn main:app --reload --port 8000",
        backend_dir
    )
    
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ 服务启动完成！")
    print("=" * 60)
    print("\n📡 服务地址:")
    print("   • AI 引擎:  http://localhost:8001")
    print("   • 后端服务: http://localhost:8000")
    print("\n🧪 测试端点:")
    print("   • AI 引擎健康检查:  http://localhost:8001/api/health")
    print("   • 后端健康检查:     http://localhost:8000/api/health")
    print("   • 生成导学步骤:     POST http://localhost:8000/api/capture/text")
    print("\n💡 提示:")
    print("   • 前端启动后，在拍照/文本输入页面测试")
    print("   • 按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    try:
        # 保持运行
        ai_process.wait()
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏸️  正在停止服务...")
        ai_process.terminate()
        backend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
