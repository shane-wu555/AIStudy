"""
后端服务主入口
FastAPI应用启动文件
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import router as api_router
from api.websocket import handle_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 后端服务启动中...")
    print("📊 初始化数据库连接...")
    print("🤖 初始化AI模型...")
    
    yield
    
    # 关闭时执行
    print("👋 后端服务关闭中...")


app = FastAPI(
    title="NumbersFallIntoPlace API",
    description="智能教育AI助手后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, tags=["API"])


# WebSocket端点
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket连接端点"""
    await handle_websocket(websocket, user_id)


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "NumbersFallIntoPlace Backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "api": "/api",
            "websocket": "/ws/{user_id}",
            "docs": "/docs",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式
        log_level="info"
    )
