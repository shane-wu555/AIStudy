"""
AI引擎主入口
独立微服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from multimodal_parser.parser import multimodal_parser, MultimodalInput, ModalityType
from reasoning_chain.engine import reasoning_engine
from knowledge_base.manager import knowledge_manager


app = FastAPI(
    title="AI Engine Service",
    description="多模态AI推理引擎",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/parse/multimodal")
async def parse_multimodal(data: dict):
    """
    多模态解析接口
    """
    multimodal_input = MultimodalInput()
    
    if "text" in data:
        multimodal_input.add_text(data["text"])
    if "image_url" in data:
        multimodal_input.add_image(data["image_url"])
    if "audio_url" in data:
        multimodal_input.add_audio(data["audio_url"])
    
    result = await multimodal_parser.parse(multimodal_input)
    return result


@app.post("/api/reasoning/execute")
async def execute_reasoning(data: dict):
    """
    执行推理
    """
    query = data.get("query", "")
    context = data.get("context", [])
    domain = data.get("domain", "general")
    
    result = await reasoning_engine.reason(query, context, domain)
    return result


@app.post("/api/knowledge/search")
async def search_knowledge(data: dict):
    """
    知识库搜索
    """
    query = data.get("query", "")
    topics = data.get("topics", [])
    subject = data.get("subject")
    method = data.get("method", "hybrid")
    
    results = await knowledge_manager.search(query, topics, subject, method)
    return {"results": results}


@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai_engine",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    return {
        "service": "AI Engine",
        "version": "1.0.0",
        "capabilities": [
            "multimodal_parsing",
            "reasoning_chain",
            "knowledge_retrieval"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
