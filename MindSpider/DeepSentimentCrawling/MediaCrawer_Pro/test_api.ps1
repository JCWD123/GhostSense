# MediaCrawer Pro API 测试脚本 (PowerShell)

$API_BASE = "http://localhost:8888"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  MediaCrawer Pro API 测试" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 健康检查
Write-Host "✅ 1. 测试健康检查..." -ForegroundColor Green
Invoke-RestMethod -Uri "$API_BASE/health" -Method Get | ConvertTo-Json -Depth 10
Write-Host ""

# 2. 获取任务列表
Write-Host "✅ 2. 获取任务列表..." -ForegroundColor Green
try {
    Invoke-RestMethod -Uri "$API_BASE/api/v1/tasks?page=1&page_size=10" -Method Get | ConvertTo-Json -Depth 10
} catch {
    Write-Host "任务列表为空或出错: $_" -ForegroundColor Yellow
}
Write-Host ""

# 3. 创建测试任务
Write-Host "✅ 3. 创建测试任务..." -ForegroundColor Green
$taskData = @{
    platform = "xhs"
    type = "search"
    keywords = @("测试", "API")
    max_count = 50
    enable_comment = $true
    enable_download = $false
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$API_BASE/api/v1/tasks" -Method Post -Body $taskData -ContentType "application/json" | ConvertTo-Json -Depth 10
} catch {
    Write-Host "创建任务出错: $_" -ForegroundColor Yellow
}
Write-Host ""

# 4. 获取账号列表
Write-Host "✅ 4. 获取账号列表..." -ForegroundColor Green
try {
    Invoke-RestMethod -Uri "$API_BASE/api/v1/accounts" -Method Get | ConvertTo-Json -Depth 10
} catch {
    Write-Host "账号列表为空或出错: $_" -ForegroundColor Yellow
}
Write-Host ""

# 5. 获取代理列表
Write-Host "✅ 5. 获取代理列表..." -ForegroundColor Green
try {
    Invoke-RestMethod -Uri "$API_BASE/api/v1/proxies" -Method Get | ConvertTo-Json -Depth 10
} catch {
    Write-Host "代理列表为空或出错: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 查看 API 文档: $API_BASE/docs" -ForegroundColor Yellow
Write-Host "🎯 健康检查: $API_BASE/health" -ForegroundColor Yellow
Write-Host ""


