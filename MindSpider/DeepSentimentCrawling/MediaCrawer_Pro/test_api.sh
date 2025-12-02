#!/bin/bash
# MediaCrawer Pro API 测试脚本

API_BASE="http://localhost:8888"

echo "=========================================="
echo "  MediaCrawer Pro API 测试"
echo "=========================================="
echo ""

# 1. 健康检查
echo "✅ 1. 测试健康检查..."
curl -s -X GET "$API_BASE/health" | python3 -m json.tool
echo ""
echo ""

# 2. 获取任务列表
echo "✅ 2. 获取任务列表..."
curl -s -X GET "$API_BASE/api/v1/tasks?page=1&page_size=10" | python3 -m json.tool
echo ""
echo ""

# 3. 创建测试任务
echo "✅ 3. 创建测试任务..."
curl -s -X POST "$API_BASE/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "type": "search",
    "keywords": ["测试", "API"],
    "max_count": 50,
    "enable_comment": true,
    "enable_download": false
  }' | python3 -m json.tool
echo ""
echo ""

# 4. 获取账号列表
echo "✅ 4. 获取账号列表..."
curl -s -X GET "$API_BASE/api/v1/accounts" | python3 -m json.tool
echo ""
echo ""

# 5. 获取代理列表
echo "✅ 5. 获取代理列表..."
curl -s -X GET "$API_BASE/api/v1/proxies" | python3 -m json.tool
echo ""
echo ""

# 6. 获取推荐流
echo "✅ 6. 获取推荐流..."
curl -s -X GET "$API_BASE/api/v1/homefeed?platform=xhs&page=1" | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "  测试完成！"
echo "=========================================="
echo ""
echo "📖 查看 API 文档: $API_BASE/docs"
echo "🎯 健康检查: $API_BASE/health"
echo ""


