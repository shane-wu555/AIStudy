#!/bin/bash

# AI引擎服务部署脚本

echo "🤖 开始部署AI引擎服务..."

cd ai_engine

# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
echo "📥 安装AI引擎依赖..."
pip install -r requirements.txt

# 3. 配置环境变量
if [ ! -f .env ]; then
    cat > .env << EOF
# AI引擎配置
AI_ENGINE_HOST=0.0.0.0
AI_ENGINE_PORT=8001

# 模型配置
DEFAULT_LLM=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4-turbo-preview

# 向量数据库
VECTOR_DB=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
EOF
    echo "✅ 已创建AI引擎配置文件"
fi

# 4. 下载模型（可选）
# echo "📦 下载预训练模型..."
# python -c "from transformers import AutoModel; AutoModel.from_pretrained('bert-base-chinese')"

# 5. 启动服务
echo "🔧 启动AI引擎服务..."
python main.py

echo "✅ AI引擎已启动在 http://localhost:8001"
