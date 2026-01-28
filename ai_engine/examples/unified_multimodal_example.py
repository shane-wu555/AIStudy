"""
集成示例: 完整的多模态可追问推理流程
展示如何结合VLM融合 + 多模态状态管理实现竞赛级架构
"""
from typing import Dict, Optional
from ai_engine.multimodal_parser.vlm_fusion import vlm_fusion_engine, CrossModalState
from ai_engine.reasoning_chain.multimodal_state import (
    multimodal_state_manager,
    MultimodalReasoningState
)
from ai_engine.reasoning_chain.engine import reasoning_engine


class UnifiedMultimodalPipeline:
    """
    统一多模态推理管道
    
    竞赛亮点:
    1. ✅ VLM原生融合: 图片像素和文本在Transformer内部交互
    2. ✅ 多模态状态维护: 可追问时保持视觉上下文一致性
    3. ✅ 显式特征对齐: 展示Vision-Text Cross-Attention
    """
    
    async def process_multimodal_query(
        self,
        session_id: str,
        user_id: str,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        audio_url: Optional[str] = None,
        is_follow_up: bool = False
    ) -> Dict:
        """
        处理多模态查询(包含可追问逻辑)
        
        示例场景:
        Round 1:
        - User: [上传图片: 几何图] "这个三角形怎么求面积?"
        - Assistant: "根据图中的底边5cm和高8cm,可以用公式S=1/2×b×h..."
        
        Round 2 (追问):
        - User: "那如果高未知呢?"
        - Assistant: [自动关联Round 1的图片] "可以用勾股定理求高..."
        """
        
        # 1. 获取多模态推理状态
        state = multimodal_state_manager.get_or_create_state(session_id, user_id)
        
        # 2. 处理指代消解(如果是追问)
        if is_follow_up and not image_url:
            # "那个三角形" → 解析为之前上传的图片
            resolved_visual = state.resolve_visual_reference(text or "")
            if resolved_visual:
                image_url = resolved_visual.image_url
                print(f"🔗 指代消解: 关联到第{state.visual_contexts.index(resolved_visual)+1}轮的图片")
        
        # 3. VLM原生融合(核心改进点1)
        vlm_result = await vlm_fusion_engine.fuse_modalities(
            vision_input=image_url,
            text_input=text,
            audio_input=audio_url,
            instruction="请理解这个数学问题并分析解题思路"
        )
        
        # 4. 构建推理链上下文(包含多模态信息)
        context_window = state.get_context_window(
            max_turns=5,
            include_visual_context=True
        )
        
        # 转换为推理引擎需要的格式
        reasoning_context = self._build_reasoning_context(
            vlm_result,
            context_window
        )
        
        # 5. 执行推理链
        reasoning_result = await reasoning_engine.reason(
            query=vlm_result["understanding"],
            context=reasoning_context,
            domain="math"
        )
        
        # 6. 更新多模态状态(核心改进点2)
        turn = state.add_turn(
            user_input={
                "text": text,
                "image": image_url,
                "audio": audio_url
            },
            assistant_output={
                "content": reasoning_result["answer"],
                "visual_commands": reasoning_result.get("visual_commands", []),
                "reasoning_trace": reasoning_result["reasoning_trace"]
            },
            cross_modal_alignment=vlm_result.get("cross_modal_alignment")
        )
        
        # 7. 持久化状态
        multimodal_state_manager.save_state(session_id)
        
        return {
            "session_id": session_id,
            "turn_id": turn.turn_id,
            "answer": reasoning_result["answer"],
            "reasoning_trace": reasoning_result["reasoning_trace"],
            "visual_commands": reasoning_result.get("visual_commands", []),
            
            # 竞赛展示点: 显式的跨模态对齐
            "cross_modal_alignment": vlm_result.get("cross_modal_alignment"),
            
            # 竞赛展示点: 多模态上下文维护
            "multimodal_context_summary": {
                "total_visual_contexts": len(state.visual_contexts),
                "total_turns": len(state.turns),
                "current_active_visual": state.active_visual_index
            },
            
            "confidence": reasoning_result.get("confidence", 0.9),
            "model_used": vlm_result.get("model_used")
        }
    
    def _build_reasoning_context(
        self,
        vlm_result: Dict,
        context_window: Dict
    ) -> list:
        """
        构建推理链上下文
        关键: 将多模态信息转换为推理引擎可用的格式
        """
        context = []
        
        # 添加历史轮次
        for turn in context_window["recent_turns"]:
            context.append({
                "role": "user",
                "content": turn["user_input"].get("text", ""),
                "has_visual": bool(turn["user_input"].get("image")),
                "visual_understanding": turn.get("cross_modal_alignment", {}).get("image_understanding", "")
            })
            context.append({
                "role": "assistant",
                "content": turn["assistant_output"]["content"]
            })
        
        # 添加当前的VLM理解结果
        context.append({
            "role": "system",
            "content": f"当前多模态理解: {vlm_result['understanding']}",
            "cross_modal_alignment": vlm_result.get("cross_modal_alignment")
        })
        
        return context


# 示例使用
async def example_multimodal_session():
    """
    演示完整的多模态可追问流程
    """
    pipeline = UnifiedMultimodalPipeline()
    
    print("=" * 80)
    print("多模态可追问推理示例")
    print("=" * 80)
    
    session_id = "demo_session_001"
    user_id = "student_123"
    
    # Round 1: 上传图片 + 提问
    print("\n【Round 1】")
    print("User: [上传几何图] 这个三角形怎么求面积?")
    
    result1 = await pipeline.process_multimodal_query(
        session_id=session_id,
        user_id=user_id,
        text="这个三角形怎么求面积?",
        image_url="http://example.com/triangle.jpg",
        is_follow_up=False
    )
    
    print(f"\nAssistant: {result1['answer']}")
    print(f"\n📊 跨模态对齐:")
    print(f"   {result1['cross_modal_alignment']}")
    print(f"\n📈 多模态上下文: {result1['multimodal_context_summary']}")
    
    # Round 2: 追问(不上传图片,但要引用Round 1的图)
    print("\n" + "="*80)
    print("\n【Round 2 - 追问】")
    print("User: 那如果我只知道三边长度呢?")
    
    result2 = await pipeline.process_multimodal_query(
        session_id=session_id,
        user_id=user_id,
        text="那如果我只知道三边长度呢?",
        is_follow_up=True  # 标记为追问
    )
    
    print(f"\nAssistant: {result2['answer']}")
    print(f"\n🔗 自动关联上下文:")
    print(f"   - 引用了第{result2['multimodal_context_summary']['current_active_visual']+1}轮的图片")
    print(f"   - 总共{result2['multimodal_context_summary']['total_turns']}轮对话")
    
    # Round 3: 继续追问
    print("\n" + "="*80)
    print("\n【Round 3 - 继续追问】")
    print("User: 用海伦公式怎么算?")
    
    result3 = await pipeline.process_multimodal_query(
        session_id=session_id,
        user_id=user_id,
        text="用海伦公式怎么算?",
        is_follow_up=True
    )
    
    print(f"\nAssistant: {result3['answer']}")
    print(f"\n✅ 多轮对话完成,视觉上下文保持一致!")


# 用于测试
if __name__ == "__main__":
    import asyncio
    asyncio.run(example_multimodal_session())
