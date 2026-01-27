"""
后端服务 - RESTful API路由
提供移动端所需的各种API接口
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

router = APIRouter()


# ============ 数据模型 ============
class CaptureRequest(BaseModel):
    """采集请求模型"""
    user_id: str
    content: str
    mode: str  # 'text', 'image', 'audio'


class SessionMessage(BaseModel):
    """会话消息模型"""
    session_id: Optional[str] = None
    user_id: str
    content: str
    step_id: Optional[str] = None  # 针对某一步骤的追问


class SessionResponse(BaseModel):
    """会话响应模型"""
    session_id: str
    message_id: str
    content: str
    reasoning: Optional[str] = None


def _demo_geometry_steps_from_text(content: str) -> List[Dict[str, Any]]:
    """根据文本问题构造一个演示用的导学步骤列表（包含几何数据）"""

    return [
        {
            "step_id": "step_understand_problem",
            "title": "读题并提取关键信息",
            "hint": content or "请先通读题目，划出已知量和待求量。",
            "type": "understand",
        },
        {
            "step_id": "step_draw_helper_line",
            "title": "画出辅助线 AC，建立空间直观",
            "hint": "在三角形中添加辅助线 AC，帮助观察角度与边长关系。",
            "type": "geometry",
            "geometry": {
                "objects": [
                    {
                        "type": "line",
                        "coords": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]],
                        "label": "辅助线 AC",
                        "step_id": "step_draw_helper_line",
                    },
                    {
                        "type": "point",
                        "coords": [[0.0, 0.0, 0.0]],
                        "label": "点 A",
                        "step_id": "step_draw_helper_line",
                    },
                    {
                        "type": "face",
                        "coords": [
                            [0.0, 0.0, 0.0],
                            [1.0, 0.0, 0.0],
                            [1.0, 1.0, 0.0],
                        ],
                        "label": "三角形 ABC 所在平面",
                        "step_id": "step_draw_helper_line",
                    },
                ]
            },
        },
        {
            "step_id": "step_solve",
            "title": "分步推导并给出中间结论",
            "hint": "先求出关键角或边，再代入原式，避免一次性跳到最终答案。",
            "type": "solve",
        },
    ]


# ============ 采集接口 ============
@router.post("/api/capture/text")
async def capture_text(request: CaptureRequest):
        """文本采集接口，返回导学步骤结构而不是单一长文本。

        前端期望结构：
        {
            "session_id": "session_xxx",
            "task_id": "capture_123",
            "steps": [
                {"step_id": "...", "title": "...", "hint": "...", "type": "...", "geometry": {...}}
            ]
        }
        """

        # TODO: 这里可以接入真正的 AI 引擎
        session_id = f"session_{request.user_id}_text"
        steps = _demo_geometry_steps_from_text(request.content)

        return {
                "session_id": session_id,
                "task_id": "capture_text_001",
                "steps": steps,
        }


@router.post("/api/capture/image")
async def capture_image(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    图像采集接口
    UC03: 多模态采集 - 拍照/相册
    """
    # TODO: 
    # 1. 保存图片到存储
    # 2. 调用VLM进行图像理解
    # 3. 返回识别结果
    
    return {
        "success": True,
        "capture_id": "capture_124",
        "image_url": f"/uploads/{file.filename}",
        "analysis": {
            "type": "math_problem",
            "confidence": 0.95,
            "extracted_text": "求解方程 x^2 + 5x + 6 = 0"
        }
    }


@router.post("/api/capture/audio")
async def capture_audio(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    语音采集接口
    UC03: 多模态采集 - 语音录制
    """
    # TODO:
    # 1. 保存音频文件
    # 2. 调用语音识别服务(ASR)
    # 3. 返回文本结果
    
    return {
        "success": True,
        "capture_id": "capture_125",
        "audio_url": f"/uploads/{file.filename}",
        "transcription": "这是语音转文字的结果"
    }


# ============ 会话接口 ============
@router.post("/api/session/message")
async def send_message(message: SessionMessage):
    """发送会话消息并返回导学结构化结果。

    当前实现为 Demo：
    - 如果 message.step_id 存在，则在对应步骤基础上做「放大讲解」。
    - 返回结构与 /api/capture/text 一致，便于前端直接用 GuidanceFlow 解析。
    """

    session_id = message.session_id or f"session_{message.user_id}_001"

    base_steps = _demo_geometry_steps_from_text(message.content)

    # 如果是针对某一步骤的追问，可以在这里根据 step_id 精细化该步
    if message.step_id:
        focus_label = f"针对 {message.step_id} 的详细讲解"
        base_steps.append(
            {
                "step_id": f"{message.step_id}_detail",
                "title": focus_label,
                "hint": "这里可以由 LLM 生成更细致的分步提示与几何说明。",
                "type": "detail",
            }
        )

    return {
        "session_id": session_id,
        "task_id": f"session_task_{session_id}",
        "steps": base_steps,
    }


@router.get("/api/session/history/{session_id}")
async def get_session_history(session_id: str):
    """
    获取会话历史
    """
    # TODO: 从数据库查询会话历史
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": "msg_001",
                "content": "您好！有什么可以帮您的？",
                "is_user": False,
                "timestamp": "2026-01-27T10:00:00"
            }
        ]
    }


@router.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """
    清空会话
    """
    # TODO: 清空数据库中的会话记录
    return {"success": True, "message": "会话已清空"}


# ============ 学习记录接口 ============
@router.get("/api/records/{user_id}")
async def get_records(user_id: str, page: int = 1, page_size: int = 20):
    """
    获取学习记录
    UC06: 学习轨迹管理
    """
    # TODO: 从数据库查询学习记录
    return {
        "total": 100,
        "page": page,
        "page_size": page_size,
        "records": [
            {
                "id": "record_001",
                "title": "解决了一道数学题",
                "description": "关于二次方程的求解",
                "type": "practice",
                "timestamp": "2026-01-27T09:00:00"
            }
        ]
    }


@router.get("/api/records/statistics/{user_id}")
async def get_statistics(user_id: str):
    """
    获取学习统计数据
    """
    # TODO: 统计用户学习数据
    return {
        "study_days": 15,
        "total_hours": 48,
        "completed_problems": 127,
        "mastered_topics": 23,
        "recent_progress": [
            {"date": "2026-01-27", "problems": 5, "time": 2.5}
        ]
    }


@router.post("/api/records")
async def add_record(user_id: str, record_data: dict):
    """
    添加学习记录
    """
    # TODO: 保存学习记录到数据库
    return {
        "success": True,
        "record_id": "record_new_001"
    }


# ============ 健康检查 ============
@router.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "backend_service",
        "version": "1.0.0"
    }
