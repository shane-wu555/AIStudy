# PowerShell版本 - Windows部署脚本

Write-Host "🚀 开始部署后端服务..." -ForegroundColor Green

# 检查Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python未安装" -ForegroundColor Red
    exit 1
}

# 进入目录
Set-Location backend_service

# 创建虚拟环境
Write-Host "📦 创建虚拟环境..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "📥 安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 创建配置文件
if (!(Test-Path .env)) {
    @"
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

DB_HOST=localhost
DB_PORT=5432
DB_NAME=numbersfall
DB_USER=postgres
DB_PASSWORD=your_password

OPENAI_API_KEY=your_openai_key
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "✅ 已创建配置文件 .env" -ForegroundColor Green
}

# 启动服务
Write-Host "🔧 启动后端服务..." -ForegroundColor Yellow
python main.py
