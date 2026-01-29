"""后端服务 - RESTful API路由

提供移动端所需的各种 API 接口,包括:
- 多模态采集/导学
- 会话与导学追问
- 学习记录管理
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import httpx
import os

from backend_service.service.records_service import (
    records_service,
    RecordType,
)

router = APIRouter()

# AI引擎服务地址
AI_ENGINE_URL = "http://localhost:8001"


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
    """文本采集接口，调用 AI 引擎生成导学步骤（含几何数据）。

    前端期望结构：
    {
      "session_id": "session_xxx",
      "task_id": "capture_123",
      "steps": [
        {"step_id": "...", "title": "...", "hint": "...", "type": "...", "geometry": {...}}
      ]
    }
    """

    try:
        # 调用 AI 引擎生成导学步骤
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AI_ENGINE_URL}/api/guidance/generate",
                json={
                    "user_id": request.user_id,
                    "content": request.content,
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # AI 引擎调用失败，返回降级方案
                return _fallback_guidance_steps(request.content, request.user_id)
                
    except Exception as e:
        print(f"调用 AI 引擎失败: {e}")
        # 降级到本地 Demo 数据
        return _fallback_guidance_steps(request.content, request.user_id)
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
    支持语音追问功能
    """
    try:
        # 读取音频文件
        audio_data = await file.read()
        
        # TODO: 保存音频文件到临时目录
        # audio_path = f"uploads/audio/{user_id}_{file.filename}"
        
        # 调用语音识别服务(ASR)
        from backend_service.utils.multimodal_processor import AudioProcessor
        transcription = AudioProcessor.transcribe_audio(audio_data, language="zh")
        
        # 将转录结果发送给AI引擎进行推理
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{AI_ENGINE_URL}/api/reasoning/process",
                    json={
                        "user_id": user_id,
                        "query": transcription,
                        "domain": "math",
                    }
                )
                
                if response.status_code == 200:
                    reasoning_result = response.json()
                else:
                    reasoning_result = None
        except Exception as e:
            print(f"调用推理引擎失败: {e}")
            reasoning_result = None
        
        return {
            "success": True,
            "capture_id": f"capture_audio_{user_id}",
            "audio_url": f"/uploads/{file.filename}",
            "transcription": transcription,
            "reasoning": reasoning_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音处理失败: {str(e)}")


@router.post("/api/capture/video")
async def capture_video(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    视频采集接口 - 长视频一键萃取
    UC03扩展: 视频内容分析和关键信息提取
    
    功能：
    1. 提取关键帧
    2. OCR识别每帧内容
    3. 提取音频并转文字
    4. 生成知识卡片
    """
    try:
        # 保存视频文件到本地,供 OpenCV 等后续处理使用
        video_data = await file.read()
        video_dir = os.path.join("uploads", "video")
        os.makedirs(video_dir, exist_ok=True)
        video_path = os.path.join(video_dir, f"{user_id}_{file.filename}")

        try:
            with open(video_path, "wb") as f:
                f.write(video_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"视频保存失败: {e}")
        
        # 调用视频处理器
        from backend_service.utils.multimodal_processor import VideoProcessor
        
        # 分析视频内容
        analysis = VideoProcessor.analyze_video_content(video_path)
        
        # 生成知识卡片
        knowledge_cards = VideoProcessor.create_knowledge_cards_from_video(analysis)
        
        return {
            "success": True,
            "capture_id": f"capture_video_{user_id}",
            # 前端可按需拼接为完整访问地址
            "video_url": f"/uploads/video/{user_id}_{file.filename}",
            "analysis": {
                "frame_count": analysis.get("frame_count", 0),
                "duration": "待实现",
                "transcription": analysis.get("transcription"),
                "detected_topics": analysis.get("detected_topics", []),
            },
            "knowledge_cards": knowledge_cards,
            "key_moments": analysis.get("key_moments", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频处理失败: {str(e)}")


@router.post("/api/video/extract-frames")
async def extract_video_frames(
    user_id: str,
    file: UploadFile = File(...),
    interval_seconds: int = 5,
    max_frames: int = 50
):
    """
    从视频中提取关键帧
    """
    try:
        from backend_service.utils.multimodal_processor import VideoProcessor
        import base64

        # 保存上传的视频到与 capture_video 相同的目录
        video_data = await file.read()
        video_dir = os.path.join("uploads", "video")
        os.makedirs(video_dir, exist_ok=True)
        video_path = os.path.join(video_dir, f"{user_id}_{file.filename}")

        try:
            with open(video_path, "wb") as f:
                f.write(video_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"视频保存失败: {e}")

        frames = VideoProcessor.extract_key_frames(
            video_path,
            interval_seconds=interval_seconds,
            max_frames=max_frames
        )
        
        return {
            "success": True,
            "frame_count": len(frames),
            "frames": [
                {
                    "timestamp": frame["timestamp"],
                    "frame_number": frame["frame_number"],
                    # 图像数据转 base64 供前端显示
                    "thumbnail": (
                        "data:image/jpeg;base64,"
                        + base64.b64encode(frame.get("image_data", b""))
                        .decode("utf-8")
                        if frame.get("image_data")
                        else ""
                    ),
                }
                for frame in frames
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"帧提取失败: {str(e)}")


# ============ 会话接口 ============
@router.post("/api/session/message")
async def send_message(message: SessionMessage):
    """发送会话消息并返回导学结构化结果。

    当前实现：
    - 如果 message.step_id 存在，则在对应步骤基础上做「放大讲解」。
    - 调用 AI 引擎生成步骤，返回结构与 /api/capture/text 一致，便于前端直接用 GuidanceFlow 解析。
    """

    try:
        # 调用 AI 引擎生成导学步骤
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AI_ENGINE_URL}/api/guidance/generate",
                json={
                    "user_id": message.user_id,
                    "content": message.content,
                    "session_id": message.session_id,
                    "step_id": message.step_id,
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # AI 引擎调用失败，返回降级方案
                session_id = message.session_id or f"session_{message.user_id}_001"
                return _fallback_guidance_steps(message.content, message.user_id, session_id, message.step_id)
                
    except Exception as e:
        print(f"调用 AI 引擎失败: {e}")
        # 降级到本地 Demo 数据
        session_id = message.session_id or f"session_{message.user_id}_001"
        return _fallback_guidance_steps(message.content, message.user_id, session_id, message.step_id)


def _fallback_guidance_steps(
    content: str,
    user_id: str,
    session_id: Optional[str] = None,
    step_id: Optional[str] = None
) -> Dict[str, Any]:
    """降级方案：当 AI 引擎不可用时，返回本地生成的导学步骤"""
    
    if not session_id:
        session_id = f"session_{user_id}_fallback"
    
    base_steps = _demo_geometry_steps_from_text(content)
    
    # 如果是追问某一步
    if step_id:
        base_steps.append({
            "step_id": f"{step_id}_detail",
            "title": f"针对「{step_id}」的详细提示",
            "hint": "这里应该由 AI 引擎生成更细致的讲解，当前为降级数据。",
            "type": "detail",
        })
    
    return {
        "session_id": session_id,
        "task_id": f"fallback_{session_id}",
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
    """获取学习记录 - UC06 学习轨迹管理。

    当前实现使用内存中的 RecordsService 作为简易存储,
    生产环境可替换为数据库/Redis 实现,保持接口兼容。
    """

    result = records_service.get_records(
        user_id=user_id,
        page=page,
        page_size=page_size,
        record_type=None,
    )
    return result


@router.get("/api/records/statistics/{user_id}")
async def get_statistics(user_id: str):
    """获取学习统计数据。"""

    return records_service.get_statistics(user_id)


@router.post("/api/records")
async def add_record(user_id: str, record_data: Dict[str, Any]):
    """添加学习记录。

    约定请求体 record_data 结构:

    ```json
    {
      "title": "看完三角形面积讲解",
      "description": "视频学习到 02:35,剩余一半",
      "type": "review",  // question/practice/review/achievement
      "metadata": {
        "video_id": "video_001",
        "last_position": 155.2
      }
    }
    ```
    """

    title = str(record_data.get("title") or "学习记录")
    description = str(record_data.get("description") or "")
    type_str = str(record_data.get("type") or RecordType.QUESTION.value)
    metadata = record_data.get("metadata") or {}

    try:
        record_type = RecordType(type_str)
    except ValueError:
        record_type = RecordType.QUESTION

    record = records_service.add_record(
        user_id=user_id,
        title=title,
        description=description,
        record_type=record_type,
        **metadata,
    )

    return {"success": True, "record": record.to_dict()}


# ============ 健康检查 ============
@router.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "backend_service",
        "version": "1.0.0"
    }
