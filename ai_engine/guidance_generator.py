"""
导学步骤生成器
根据题目/问题生成结构化导学步骤，包含几何可视化数据
"""
from typing import List, Dict, Any, Optional
import uuid


class GuidanceGenerator:
    """导学步骤生成器"""
    
    def __init__(self):
        self.session_store: Dict[str, Dict] = {}
    
    async def generate_guidance_steps(
        self,
        user_id: str,
        content: str,
        session_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        生成导学步骤
        
        Args:
            user_id: 用户ID
            content: 问题内容
            session_id: 会话ID（追问时提供）
            step_id: 步骤ID（针对某一步追问时提供）
            
        Returns:
            {
                "session_id": "...",
                "task_id": "...",
                "steps": [
                    {
                        "step_id": "...",
                        "title": "...",
                        "hint": "...",
                        "type": "...",
                        "geometry": {...}
                    }
                ]
            }
        """
        
        # 生成或获取 session_id
        if not session_id:
            session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # TODO: 这里可以调用 LLM 分析题目并生成步骤
        # 当前先用一个智能一点的 Demo 实现
        
        if step_id:
            # 如果是针对某个步骤的追问，生成该步骤的详细讲解
            steps = await self._generate_detail_steps(content, step_id)
        else:
            # 首次生成导学步骤
            steps = await self._generate_initial_steps(content)
        
        result = {
            "session_id": session_id,
            "task_id": f"task_{uuid.uuid4().hex[:12]}",
            "steps": steps,
        }
        
        # 保存到会话存储
        self.session_store[session_id] = result
        
        return result
    
    async def _generate_initial_steps(self, content: str) -> List[Dict[str, Any]]:
        """生成初始导学步骤（包含几何数据）"""
        
        # 分析题目类型（简单启发式判断，实际应该用 LLM）
        is_geometry_problem = any(
            keyword in content
            for keyword in ["三角形", "四边形", "圆", "立方体", "平面", "辅助线", "几何"]
        )
        
        steps = [
            {
                "step_id": "step_read_problem",
                "title": "📖 第一步：读懂题目",
                "hint": f"原题：{content}\n\n请先用自己的话复述一遍，确保理解了题目要求。",
                "type": "understand",
            }
        ]
        
        if is_geometry_problem:
            # 几何题：生成画图步骤 + 3D 几何数据
            steps.append({
                "step_id": "step_draw_diagram",
                "title": "📐 第二步：画出图形并标注",
                "hint": "在纸上（或脑海中）画出题目描述的几何图形，标出已知的点、线、面。下方的 3D 演示可以帮你建立空间感。",
                "type": "geometry",
                "geometry": self._generate_geometry_demo(content),
            })
            
            steps.append({
                "step_id": "step_find_relation",
                "title": "🔍 第三步：找出几何关系",
                "hint": "观察图形中的角度、边长、面积等要素之间的关系。有时需要添加辅助线来构造特殊三角形或发现隐藏关系。",
                "type": "analysis",
            })
            
            steps.append({
                "step_id": "step_solve",
                "title": "✍️ 第四步：列式求解",
                "hint": "根据几何关系列出方程或比例式，逐步求出未知量。记得每一步都写清楚理由。",
                "type": "solve",
            })
        else:
            # 非几何题：通用步骤
            steps.extend([
                {
                    "step_id": "step_list_knowns",
                    "title": "📝 第二步：列出已知和未知",
                    "hint": "把题目给出的条件（已知）和需要求的量（未知）分别列出来。",
                    "type": "analysis",
                },
                {
                    "step_id": "step_choose_method",
                    "title": "💡 第三步：选择解题方法",
                    "hint": "想一想可以用哪些方法：代数、图像、公式、或者分类讨论？先选一个最有把握的试试。",
                    "type": "method",
                },
                {
                    "step_id": "step_try_solve",
                    "title": "✍️ 第四步：动手尝试",
                    "hint": "开始解题！遇到卡顿的地方，可以点击「追问」按钮获得提示。",
                    "type": "solve",
                },
            ])
        
        steps.append({
            "step_id": "step_verify",
            "title": "✅ 最后一步：检验答案",
            "hint": "把答案代回原题检验，或者换个方法再算一遍，确保结果正确。",
            "type": "verify",
        })
        
        return steps
    
    async def _generate_detail_steps(
        self,
        content: str,
        parent_step_id: str
    ) -> List[Dict[str, Any]]:
        """针对某一步骤生成更详细的子步骤"""
        
        # TODO: 这里可以根据 parent_step_id 和 content 调用 LLM 生成更细致的讲解
        
        return [
            {
                "step_id": f"{parent_step_id}_detail_1",
                "title": f"📌 关于「{parent_step_id}」的详细提示",
                "hint": "这一步的核心是理解题目中隐含的条件。试着把抽象的描述转化为具体的图形或公式。",
                "type": "detail",
            },
            {
                "step_id": f"{parent_step_id}_detail_2",
                "title": "🔍 常见误区提醒",
                "hint": "注意不要遗漏单位、符号，以及边界情况（比如分母为 0、负数开方等）。",
                "type": "hint",
            },
            {
                "step_id": f"{parent_step_id}_example",
                "title": "📚 相似例题参考",
                "hint": "可以回忆一下之前做过的类似题目，或者查阅教材中的例题。",
                "type": "example",
            },
        ]
    
    def _generate_geometry_demo(self, content: str) -> Dict[str, Any]:
        """生成几何演示数据（3D 对象）"""
        
        # TODO: 实际应该根据题目解析出具体的几何对象
        # 这里先返回一个通用的"辅助线 + 点 + 面"组合示例
        
        return {
            "objects": [
                {
                    "type": "line",
                    "coords": [[0.0, 0.0, 0.0], [1.2, 1.2, 0.8]],
                    "label": "辅助线 AC",
                    "step_id": "step_draw_diagram",
                    "color": "#1E88E5",
                },
                {
                    "type": "point",
                    "coords": [[0.0, 0.0, 0.0]],
                    "label": "点 A",
                    "step_id": "step_draw_diagram",
                },
                {
                    "type": "point",
                    "coords": [[1.2, 1.2, 0.8]],
                    "label": "点 C",
                    "step_id": "step_draw_diagram",
                },
                {
                    "type": "face",
                    "coords": [
                        [0.0, 0.0, 0.0],
                        [1.2, 0.0, 0.0],
                        [1.2, 1.2, 0.0],
                        [0.0, 1.2, 0.0],
                    ],
                    "label": "底面 ABCD",
                    "step_id": "step_draw_diagram",
                    "color": "#FFA726",
                },
            ]
        }


# 全局实例
guidance_generator = GuidanceGenerator()
