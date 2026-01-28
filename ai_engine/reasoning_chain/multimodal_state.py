"""
多模态推理状态管理
核心: 在可追问对话中维护多模态上下文的一致性
"""
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid


@dataclass
class VisualContext:
    """视觉上下文"""
    image_url: str
    image_description: str  # VLM生成的描述
    detected_objects: List[Dict] = field(default_factory=list)  # 检测到的对象
    extracted_text: Optional[str] = None  # OCR提取的文本(补充)
    visual_embeddings: Optional[List[float]] = None  # 视觉特征向量
    referenced_in_turns: List[int] = field(default_factory=list)  # 在哪些轮次被引用
    
    def to_dict(self) -> Dict:
        return {
            "image_url": self.image_url,
            "description": self.image_description,
            "detected_objects": self.detected_objects,
            "extracted_text": self.extracted_text,
            "referenced_in_turns": self.referenced_in_turns
        }


@dataclass
class AudioContext:
    """音频上下文"""
    audio_url: str
    transcription: str  # ASR转录
    speaker_info: Optional[Dict] = None  # 说话人信息
    emotion: Optional[str] = None  # 情感分析
    referenced_in_turns: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "audio_url": self.audio_url,
            "transcription": self.transcription,
            "speaker_info": self.speaker_info,
            "emotion": self.emotion,
            "referenced_in_turns": self.referenced_in_turns
        }


@dataclass
class ReasoningTurn:
    """推理轮次"""
    turn_id: int
    user_input: Dict  # {"text": "...", "image": "...", "audio": "..."}
    assistant_output: Dict  # {"content": "...", "visual_commands": [...]}
    cross_modal_alignment: Optional[Dict] = None  # VLM的跨模态对齐结果
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "turn_id": self.turn_id,
            "user_input": self.user_input,
            "assistant_output": self.assistant_output,
            "cross_modal_alignment": self.cross_modal_alignment,
            "timestamp": self.timestamp.isoformat()
        }


class MultimodalReasoningState:
    """
    多模态推理状态
    
    核心功能:
    1. 维护多轮对话中的视觉/音频上下文
    2. 追踪哪些模态在哪些轮次被使用
    3. 实现指代消解("那个三角形"指的是第1轮上传的图)
    """
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 多模态上下文池
        self.visual_contexts: List[VisualContext] = []  # 所有上传的图片
        self.audio_contexts: List[AudioContext] = []    # 所有上传的音频
        
        # 推理轮次历史
        self.turns: List[ReasoningTurn] = []
        
        # 当前活跃的模态索引
        self.active_visual_index: Optional[int] = None  # 当前正在讨论的图片
        self.active_audio_index: Optional[int] = None
    
    def add_turn(
        self,
        user_input: Dict,
        assistant_output: Dict,
        cross_modal_alignment: Optional[Dict] = None
    ) -> ReasoningTurn:
        """
        添加推理轮次
        
        Args:
            user_input: {
                "text": "这个三角形怎么求面积?",
                "image": "http://...",  # 可选
                "audio": "http://..."   # 可选
            }
            assistant_output: {
                "content": "...",
                "visual_commands": [...]
            }
            cross_modal_alignment: VLM返回的跨模态对齐信息
        """
        turn_id = len(self.turns) + 1
        turn = ReasoningTurn(
            turn_id=turn_id,
            user_input=user_input,
            assistant_output=assistant_output,
            cross_modal_alignment=cross_modal_alignment
        )
        
        # 处理新的视觉输入
        if user_input.get("image"):
            visual_ctx = VisualContext(
                image_url=user_input["image"],
                image_description=cross_modal_alignment.get("image_understanding", "") if cross_modal_alignment else "",
                detected_objects=cross_modal_alignment.get("detected_objects", []) if cross_modal_alignment else []
            )
            visual_ctx.referenced_in_turns.append(turn_id)
            self.visual_contexts.append(visual_ctx)
            self.active_visual_index = len(self.visual_contexts) - 1
        
        # 处理新的音频输入
        if user_input.get("audio"):
            audio_ctx = AudioContext(
                audio_url=user_input["audio"],
                transcription=user_input.get("audio_transcription", "")
            )
            audio_ctx.referenced_in_turns.append(turn_id)
            self.audio_contexts.append(audio_ctx)
            self.active_audio_index = len(self.audio_contexts) - 1
        
        self.turns.append(turn)
        self.updated_at = datetime.now()
        
        return turn
    
    def resolve_visual_reference(self, text_query: str) -> Optional[VisualContext]:
        """
        解析视觉指代
        
        例子:
        - "那个三角形" → 找到最近提到三角形的图片
        - "第一张图" → 返回visual_contexts[0]
        - "刚才的图" → 返回active_visual_index对应的图
        """
        if not self.visual_contexts:
            return None
        
        # 简单规则(实际应使用NLP):
        if "第一" in text_query or "最开始" in text_query:
            return self.visual_contexts[0]
        elif "那个" in text_query or "这个" in text_query or "刚才" in text_query:
            # 返回当前活跃的图片
            if self.active_visual_index is not None:
                return self.visual_contexts[self.active_visual_index]
        
        # 默认返回最新的
        return self.visual_contexts[-1] if self.visual_contexts else None
    
    def get_context_window(
        self,
        max_turns: int = 5,
        include_visual_context: bool = True
    ) -> Dict:
        """
        获取多模态上下文窗口
        
        与纯文本对话的区别:
        - 纯文本: 只返回最近N条消息
        - 多模态: 还要包含被引用的图片/音频上下文
        
        Returns:
            {
                "recent_turns": [...],  # 最近N轮对话
                "visual_contexts": [...],  # 被引用的图片
                "audio_contexts": [...]    # 被引用的音频
            }
        """
        recent_turns = self.turns[-max_turns:]
        
        # 收集这些轮次中引用的所有视觉/音频上下文
        referenced_visual_ids = set()
        referenced_audio_ids = set()
        
        for turn in recent_turns:
            # 检查哪些视觉上下文在这些轮次中被引用
            for i, visual_ctx in enumerate(self.visual_contexts):
                if turn.turn_id in visual_ctx.referenced_in_turns:
                    referenced_visual_ids.add(i)
            
            for i, audio_ctx in enumerate(self.audio_contexts):
                if turn.turn_id in audio_ctx.referenced_in_turns:
                    referenced_audio_ids.add(i)
        
        return {
            "recent_turns": [turn.to_dict() for turn in recent_turns],
            "visual_contexts": [
                self.visual_contexts[i].to_dict()
                for i in sorted(referenced_visual_ids)
            ] if include_visual_context else [],
            "audio_contexts": [
                self.audio_contexts[i].to_dict()
                for i in sorted(referenced_audio_ids)
            ],
            "active_visual": self.visual_contexts[self.active_visual_index].to_dict() 
                if self.active_visual_index is not None else None
        }
    
    def mark_visual_referenced(self, visual_index: int, turn_id: int):
        """标记某个图片在某轮被引用"""
        if 0 <= visual_index < len(self.visual_contexts):
            self.visual_contexts[visual_index].referenced_in_turns.append(turn_id)
            self.active_visual_index = visual_index
    
    def get_full_state(self) -> Dict:
        """获取完整状态(用于持久化)"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "visual_contexts": [ctx.to_dict() for ctx in self.visual_contexts],
            "audio_contexts": [ctx.to_dict() for ctx in self.audio_contexts],
            "turns": [turn.to_dict() for turn in self.turns],
            "active_visual_index": self.active_visual_index,
            "active_audio_index": self.active_audio_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MultimodalReasoningState":
        """从字典恢复状态"""
        state = cls(data["session_id"], data["user_id"])
        # TODO: 完整的反序列化逻辑
        return state


class MultimodalStateManager:
    """多模态状态管理器"""
    
    def __init__(self):
        self.states: Dict[str, MultimodalReasoningState] = {}
    
    def get_or_create_state(
        self,
        session_id: str,
        user_id: str
    ) -> MultimodalReasoningState:
        """获取或创建状态"""
        if session_id not in self.states:
            self.states[session_id] = MultimodalReasoningState(session_id, user_id)
        return self.states[session_id]
    
    def save_state(self, session_id: str):
        """持久化状态(可存到Redis/数据库)"""
        if session_id in self.states:
            state_dict = self.states[session_id].get_full_state()
            # TODO: 保存到数据库
            # db.save("multimodal_states", session_id, state_dict)
            pass
    
    def load_state(self, session_id: str) -> Optional[MultimodalReasoningState]:
        """加载状态"""
        # TODO: 从数据库加载
        # state_dict = db.load("multimodal_states", session_id)
        # return MultimodalReasoningState.from_dict(state_dict)
        return self.states.get(session_id)


# 全局状态管理器
multimodal_state_manager = MultimodalStateManager()
