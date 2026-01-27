#!/bin/bash

# 后端服务部署脚本

echo "🚀 开始部署后端服务..."

# 1. 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 2. 创建虚拟环境
echo "📦 创建Python虚拟环境..."
cd backend_service
python3 -m venv venv
source venv/bin/activate  # Windows使用: venv\Scripts\activate

# 3. 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 4. 配置环境变量
echo "⚙️ 配置环境变量..."
if [ ! -f .env ]; then
    cat > .env << EOF
# 后端服务配置
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=numbersfall
DB_USER=postgres
DB_PASSWORD=your_password

# AI模型配置
OPENAI_API_KEY=your_openai_key
WENXIN_API_KEY=your_wenxin_key

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
    echo "✅ 已创建 .env 配置文件，请填写实际配置"
fi

# 5. 启动服务
echo "🔧 启动后端服务..."
python main.py

echo "✅ 后端服务已启动在 http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
