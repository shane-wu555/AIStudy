"""
导学调度服务
负责管理学习会话、上下文管理、多轮对话逻辑
"""
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class SessionContext:
    """会话上下文"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata: Dict = {}
    
    def add_message(self, role: str, content: str, **kwargs):
        """添加消息到上下文"""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_window(self, max_messages: int = 10) -> List[Dict]:
        """获取上下文窗口（最近N条消息）"""
        return self.messages[-max_messages:]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


class TutoringService:
    """导学服务"""
    
    def __init__(self):
        # 内存存储会话（生产环境应使用Redis或数据库）
        self.sessions: Dict[str, SessionContext] = {}
    
    def get_or_create_session(self, user_id: str, session_id: Optional[str] = None) -> SessionContext:
        """获取或创建会话"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # 创建新会话
        new_session_id = session_id or f"session_{user_id}_{uuid.uuid4().hex[:8]}"
        session = SessionContext(new_session_id, user_id)
        self.sessions[new_session_id] = session
        
        # 添加欢迎消息
        session.add_message(
            "assistant",
            "您好！我是AI导学助手，有什么可以帮您的吗？"
        )
        
        return session
    
    async def process_user_message(
        self,
        session_id: str,
        user_id: str,
        content: str
    ) -> Dict:
        """
        处理用户消息
        UC04: 智能导学对话
        """
        # 获取会话
        session = self.get_or_create_session(user_id, session_id)
        
        # 添加用户消息
        user_msg = session.add_message("user", content)
        
        # TODO: 调用AI引擎生成回复
        # 1. 获取上下文窗口
        context = session.get_context_window()
        
        # 2. 调用model_interface获取AI回复
        ai_response = await self._call_ai_engine(content, context)
        
        # 3. 添加AI回复到上下文
        assistant_msg = session.add_message(
            "assistant",
            ai_response["content"],
            reasoning=ai_response.get("reasoning"),
            confidence=ai_response.get("confidence")
        )
        
        return {
            "session_id": session.session_id,
            "message_id": assistant_msg["id"],
            "content": assistant_msg["content"],
            "reasoning": assistant_msg.get("reasoning"),
            "timestamp": assistant_msg["timestamp"]
        }
    
    async def _call_ai_engine(self, query: str, context: List[Dict]) -> Dict:
        """
        调用AI引擎
        TODO: 实际实现中应调用model_interface
        """
        # 模拟AI回复
        return {
            "content": f"关于您的问题 '{query}'，这是AI的回答...",
            "reasoning": "推理链: 问题分析 → 知识检索 → 答案生成 → 验证",
            "confidence": 0.85
        }
    
    def get_session_history(self, session_id: str) -> Optional[Dict]:
        """获取会话历史"""
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None
    
    def clear_session(self, session_id: str) -> bool:
        """清空会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.sessions)


# 全局服务实例
tutoring_service = TutoringService()
