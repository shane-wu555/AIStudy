"""导学调度服务

负责管理学习会话、上下文管理、多轮对话逻辑,并维护简单的
"ReasoningState" 以支持可追问场景,例如:

- 上一轮建议画出辅助线 AC
- 本轮语音追问: "为什么要连这一条?"
- 系统需要基于缓存的 visual_commands 做出解释
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
        self.metadata: Dict = {
            # 最近一轮 AI 返回的可视化指令,用于可追问场景
            "last_visual_commands": [],
        }
    
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
        content: str,
        *,
        modality: str = "text",
        visual_commands: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        处理用户消息
        UC04: 智能导学对话
        """
        # 获取会话
        session = self.get_or_create_session(user_id, session_id)
        
        # 如果本轮携带了新的可视化指令(例如由前端通过 AI 推理返回),
        # 则记录到会话的 ReasoningState 中,用于后续追问解释
        if visual_commands:
            session.metadata["last_visual_commands"] = visual_commands

        # 添加用户消息
        user_msg = session.add_message("user", content, modality=modality)
        
        # TODO: 调用AI引擎生成回复
        # 1. 获取上下文窗口
        context = session.get_context_window()

        # 2. 调用 AI 引擎/本地推理逻辑
        ai_response = await self._call_ai_engine(content, context, session)
        
        # 3. 添加AI回复到上下文
        assistant_msg = session.add_message(
            "assistant",
            ai_response["content"],
            reasoning=ai_response.get("reasoning"),
            confidence=ai_response.get("confidence"),
            visual_commands=ai_response.get("visual_commands"),
        )

        # 同步更新 ReasoningState 中最近的 visual_commands
        if ai_response.get("visual_commands"):
            session.metadata["last_visual_commands"] = ai_response["visual_commands"]
        
        return {
            "session_id": session.session_id,
            "message_id": assistant_msg["id"],
            "content": assistant_msg["content"],
            "reasoning": assistant_msg.get("reasoning"),
            "timestamp": assistant_msg["timestamp"]
        }
    
    async def _call_ai_engine(
        self,
        query: str,
        context: List[Dict],
        session: SessionContext,
    ) -> Dict:
        """调用 AI 引擎或使用本地规则生成回复。

        当前实现采用"规则 + 占位"的方式模拟:
        - 如果检测到是关于"为什么要连这条辅助线"的追问,
          将优先使用缓存的 visual_commands 给出解释。
        - 否则返回一个通用回答。

        实际接入时,可以在这里调用后端统一的 model_interface
        或 AI 引擎推理服务,并把返回的 visual_commands 写入 session.metadata。
        """

        normalized_query = query.strip()
        last_visual_commands: List[Dict] = session.metadata.get(
            "last_visual_commands", []
        ) or []

        # 场景: 用户追问"为什么要连这一条?"且上一轮有辅助线指令
        if (
            last_visual_commands
            and any(
                kw in normalized_query
                for kw in ["为什么要连", "为什么连", "为什么要画", "为什么要加这一条"]
            )
        ):
            # 取第一条 draw_line 指令作为解释依据
            helper_line = None
            for cmd in last_visual_commands:
                if cmd.get("type") == "draw_line":
                    helper_line = cmd
                    break

            reason = (
                helper_line.get("reason")
                if helper_line and helper_line.get("reason")
                else "因为连接 AC 后可以构造全等三角形,从而把复杂图形拆解为更容易计算的部分。"
            )

            return {
                "content": reason,
                "reasoning": "基于上一轮的 visual_commands 进行解释,突出辅助线在构造全等/相似三角形中的作用。",
                "confidence": 0.9,
                "visual_commands": last_visual_commands,
            }

        # 默认占位实现: 简单的通用回答
        return {
            "content": f"关于您的问题 '{query}'，这是AI的回答(占位)...",
            "reasoning": "推理链: 问题分析 → 知识检索 → 答案生成 → 验证",
            "confidence": 0.85,
            # 示例: 如果没有历史可用,构造一条演示用辅助线指令,方便前端联调
            "visual_commands": [
                {
                    "type": "draw_line",
                    "from": "A",
                    "to": "C",
                    "color": "red",
                    "animate": True,
                    "label": "辅助线 AC",
                    "reason": "连接 AC 可以把原三角形分解成两个更易分析的三角形,便于使用全等与相似关系。",
                }
            ],
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
