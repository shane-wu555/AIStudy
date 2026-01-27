"""
WebSocket处理 - 实时通信
支持实时消息推送和双向通信
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活动连接: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """接受新连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"用户 {user_id} 已连接 WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"用户 {user_id} 已断开 WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """发送个人消息"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            
            # 清理断开的连接
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, user_id: str):
    """
    处理WebSocket连接
    用于实时会话、进度推送等
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            msg_type = message.get("type")
            
            if msg_type == "chat":
                # 处理聊天消息
                response = await process_chat_message(message, user_id)
                await manager.send_personal_message(response, user_id)
            
            elif msg_type == "ping":
                # 心跳检测
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": message.get("timestamp")},
                    user_id
                )
            
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "未知消息类型"},
                    user_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(websocket, user_id)


async def process_chat_message(message: dict, user_id: str) -> dict:
    """
    处理聊天消息
    TODO: 集成AI引擎
    """
    content = message.get("content", "")
    
    # 模拟AI处理延迟
    await asyncio.sleep(1)
    
    # TODO: 调用AI引擎生成回复
    return {
        "type": "chat_response",
        "content": f"AI回复: 收到您的消息 '{content}'",
        "timestamp": message.get("timestamp"),
        "reasoning": "推理链路: 理解 → 检索 → 生成"
    }


async def send_progress_update(user_id: str, progress: int, message: str):
    """
    发送进度更新
    用于长时间任务的进度通知
    """
    await manager.send_personal_message({
        "type": "progress",
        "progress": progress,
        "message": message
    }, user_id)
