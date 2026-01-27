from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import uuid
import time

app = FastAPI(title="数到渠成 AI 导学系统")

# 定义响应模型
class UploadResponse(BaseModel):
    task_id: str
    timestamp: float
    status: str

@app.post("/upload/capture", response_model=UploadResponse)
async def upload_capture(
    file: UploadFile = File(...),         # 接收图片或音频文件
    mode: str = Form(...),                # 'image' (拍照) 或 'audio' (语音提问)
    user_id: str = Form(...),             # 用户标识
    session_id: str = Form(None)          # 如果是追问，则带上会话ID
):
    """
    接收移动端上传的题目图片或语音提问
    """
    # 1. 生成唯一任务ID
    task_id = str(uuid.uuid4())
    
    # 2. 模拟保存文件（实际开发中应存入对象存储如 OSS/S3）
    file_location = f"temp_storage/{task_id}_{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
        
    print(f"收到来自用户 {user_id} 的 {mode} 请求，已保存至 {file_location}")

    return {
        "task_id": task_id,
        "timestamp": time.time(),
        "status": "received"
    }