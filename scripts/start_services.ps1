# 快速启动脚本
# 一键启动 AI 引擎 + 后端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 数到渠成 - AI 导学系统启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$workspace = $PSScriptRoot | Split-Path -Parent

# 启动 AI 引擎服务 (端口 8001)
Write-Host "🚀 正在启动 AI 引擎服务..." -ForegroundColor Green
$aiEngine = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "$workspace\ai_engine" -PassThru -WindowStyle Normal

Start-Sleep -Seconds 2

# 启动后端服务 (端口 8000)
Write-Host "🚀 正在启动后端服务..." -ForegroundColor Green
$backend = Start-Process -FilePath "python" -ArgumentList "-m","uvicorn","api.main:app","--reload","--port","8000" -WorkingDirectory "$workspace\backend_service" -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 服务地址:" -ForegroundColor Yellow
Write-Host "   • AI 引擎:  http://localhost:8001" -ForegroundColor White
Write-Host "   • 后端服务: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🧪 测试端点:" -ForegroundColor Yellow
Write-Host "   • AI 引擎健康检查:  http://localhost:8001/api/health" -ForegroundColor White
Write-Host "   • 后端健康检查:     http://localhost:8000/api/health" -ForegroundColor White
Write-Host "   • 生成导学步骤:     POST http://localhost:8000/api/capture/text" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示:" -ForegroundColor Yellow
Write-Host "   • 现在可以启动 Flutter 前端测试完整链路" -ForegroundColor White
Write-Host "   • 按任意键停止所有服务" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 等待用户输入
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "⏸️  正在停止服务..." -ForegroundColor Yellow
Stop-Process -Id $aiEngine.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
Write-Host "✅ 服务已停止" -ForegroundColor Green
