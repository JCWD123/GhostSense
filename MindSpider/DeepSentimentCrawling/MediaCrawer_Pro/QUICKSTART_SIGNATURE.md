# 🚀 签名服务快速启动指南

## 📌 5分钟快速上手

修复后的签名服务现在完全支持小红书评论接口！按照以下步骤快速开始：

---

## 步骤1: 启动签名服务 ⚡

```bash
cd MediaCrawer_Pro/signature-service

# 安装依赖（首次运行）
npm install

# 启动服务
node src/api/server.js
```

**预期输出：**
```
🚀 ========================================
📦 MediaCrawler 签名服务已启动
🌐 监听地址: http://0.0.0.0:3100
📚 API 文档:
   - 纯JS签名: POST /sign/xhs
   - 浏览器模式: POST /sign/xhs/browser
   - 混合模式: POST /sign/xhs/hybrid
   - 健康检查: GET /health
🎯 版本: 2.0.0 (支持 Playwright + Electron)
========================================
```

---

## 步骤2: 验证服务 ✅

### 方法1: 浏览器访问
打开浏览器访问：`http://localhost:3100/health`

### 方法2: 命令行测试
```bash
# 健康检查
curl http://localhost:3100/health

# 测试基础签名
curl -X POST http://localhost:3100/sign/xhs \
  -H "Content-Type: application/json" \
  -d '{"url":"/api/sns/web/v1/search/notes","method":"POST","a1":"test_a1"}'
```

### 方法3: 运行测试脚本
```bash
cd MediaCrawer_Pro/signature-service
node test_signature_fix.js
```

---

## 步骤3: 获取必要参数 🔑

### 3.1 获取 Cookie (a1)

**方法A: 从浏览器复制**
1. 登录小红书网站：https://www.xiaohongshu.com
2. 打开开发者工具（F12）
3. 进入 Application → Cookies → https://www.xiaohongshu.com
4. 复制 `a1` 的值

**方法B: 从网络请求复制**
1. 打开开发者工具（F12）→ Network
2. 刷新页面或搜索笔记
3. 点击任意 XHR 请求
4. 在 Headers 中找到 Cookie，复制 `a1=...` 部分

### 3.2 获取 localStorage b1

在小红书网站的浏览器控制台（F12）中执行：
```javascript
localStorage.getItem('b1')
```

复制输出的值。

### 3.3 获取笔记的 xsec_token

**方法A: 从URL复制**
```
https://www.xiaohongshu.com/explore/66fad51c000000001b0224b8?xsec_token=AB3rO-QopW5sgrJ41GwN01WCXh6yWPxjSoFI9D5JIMgKw=&xsec_source=pc_search
                                                             ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                                             复制这部分
```

**方法B: 从搜索结果获取**
搜索笔记后，每个笔记的URL都包含 `xsec_token`。

---

## 步骤4: 使用完整签名 🎯

### 4.1 Python 调用示例

```python
import asyncio
from backend.crawler.xhs_client import XHSClient
from backend.crawler.xhs_helper import parse_note_info_from_note_url

async def get_comments():
    # 1. 初始化客户端
    client = XHSClient()
    
    # 2. 设置 Cookie（替换为你的真实值）
    client.set_cookie("a1=你的a1值; webId=你的webId值")
    
    # 3. 解析笔记URL（替换为真实URL）
    note_url = "https://www.xiaohongshu.com/explore/笔记ID?xsec_token=令牌&xsec_source=pc_search"
    note_info = parse_note_info_from_note_url(note_url)
    
    # 4. 获取评论（✅ 现在会自动使用完整签名）
    comments = await client.get_note_comments(
        note_id=note_info.note_id,
        xsec_token=note_info.xsec_token,
        xsec_source=note_info.xsec_source
    )
    
    print(f"✅ 获取到 {len(comments['comments'])} 条评论")
    return comments

# 运行
asyncio.run(get_comments())
```

### 4.2 HTTP API 直接调用

**基础签名（搜索等低安全接口）：**
```bash
curl -X POST http://localhost:3100/sign/xhs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/api/sns/web/v1/search/notes",
    "method": "POST",
    "a1": "你的a1值"
  }'
```

**完整签名（评论等高安全接口）⭐：**
```bash
curl -X POST http://localhost:3100/sign/xhs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/api/sns/web/v2/comment/page",
    "method": "GET",
    "a1": "你的a1值",
    "b1": "你的b1值"
  }'
```

---

## 常见使用场景 📚

### 场景1: 搜索笔记 🔍
```python
# 不需要 b1，使用基础签名
headers = await signature_client.get_xhs_sign(
    url="/api/sns/web/v1/search/notes",
    method="POST",
    data={"keyword": "python"},
    a1=your_a1
)
```

### 场景2: 获取笔记详情 📄
```python
# 建议传入 b1，获取完整签名
headers = await signature_client.get_xhs_sign(
    url="/api/sns/web/v1/feed",
    method="POST",
    data={"source_note_id": note_id},
    a1=your_a1,
    b1=your_b1  # ⚠️ 建议传入
)
```

### 场景3: 获取评论 💬 ⚠️ 必需完整签名
```python
from backend.crawler.xhs_helper import parse_note_info_from_note_url

# 1. 解析URL获取 xsec_token
note_info = parse_note_info_from_note_url(note_url)

# 2. 获取评论（必需传入 b1）
comments = await client.get_note_comments(
    note_id=note_info.note_id,
    xsec_token=note_info.xsec_token,  # ⚠️ 必需
    xsec_source=note_info.xsec_source
)
```

### 场景4: 获取视频链接 🎬
```python
# 修复后的视频接口
video_url = await client.get_video_play_url(
    video_id="你的video_id",
    note_id="笔记ID"
)
```

---

## 三种签名模式对比 📊

| 模式 | 传入参数 | 返回字段 | 耗时 | 适用场景 |
|------|---------|---------|------|---------|
| **纯JS** | url, method, a1 | x-s, x-t | ~50ms | 搜索、列表 |
| **JS增强** ⭐ | url, method, a1, **b1** | x-s, x-t, x-s-common, X-B3-Traceid | ~100ms | **评论、详情** |
| **Playwright** | url, method, cookie | 完整请求头 | ~2000ms | 调试、最高安全 |

**推荐：** 优先使用 **JS增强模式**（传入b1参数），性能好且功能完整。

---

## 故障排查 🔧

### 问题1: 评论接口返回 461/403

**原因：** 缺少完整签名

**解决：**
```python
# ❌ 错误（缺少 b1）
headers = await signature_client.get_xhs_sign(url, a1=a1)

# ✅ 正确（传入 b1）
headers = await signature_client.get_xhs_sign(url, a1=a1, b1=b1)
```

### 问题2: 找不到 xsec_token

**原因：** 笔记URL不完整

**解决：**
```python
# 使用辅助函数解析
from backend.crawler.xhs_helper import parse_note_info_from_note_url

note_info = parse_note_info_from_note_url(完整的笔记URL)
```

### 问题3: 签名服务连接失败

**检查：**
```bash
# 1. 确认服务是否运行
curl http://localhost:3100/health

# 2. 检查配置
# backend/core/config.py 中确认：
SIGNATURE_SERVICE_URL = "http://localhost:3100"
```

### 问题4: 视频链接无法播放

**检查：**
```python
# 确保使用修复后的代码
# API路径应该是：
uri = "/api/sns/v1/resource/video/play"  # ✅ 正确（v1，不是web/v1）
data = {"video_id": video_id, "source": "pc"}  # ✅ 正确（pc，不是pc_web）
```

---

## 性能优化建议 ⚡

### 1. 缓存 b1 值
```python
# b1 长期有效，可以缓存
import json

# 保存
with open('config.json', 'w') as f:
    json.dump({"b1": b1_value}, f)

# 读取
with open('config.json', 'r') as f:
    config = json.load(f)
    b1 = config.get('b1')
```

### 2. 复用客户端实例
```python
# ✅ 好的做法
async with XHSClient() as client:
    client.set_cookie(cookie)
    
    # 批量请求
    for note_id in note_ids:
        comments = await client.get_note_comments(...)
        await asyncio.sleep(0.5)  # 礼貌延迟
```

### 3. 使用连接池
```python
# 签名服务会自动复用HTTP连接
# 无需额外配置
```

---

## 下一步 🎓

1. **阅读详细文档：**
   - 📄 `docs/如何切换签名模式.md` - 所有模式的详细说明
   - 📄 `SIGNATURE_FIX_SUMMARY.md` - 完整修复总结

2. **运行示例代码：**
   ```bash
   python examples/xhs_comment_example.py
   ```

3. **测试自己的场景：**
   - 搜索笔记
   - 获取评论
   - 下载视频

4. **阅读 API 文档：**
   - 📄 `docs/API接口修复说明.md`

---

## 🎉 完成！

现在你已经可以使用修复后的签名服务了！

**关键要点：**
- ✅ 评论接口必须传入 `b1` 和 `xsec_token`
- ✅ 优先使用 JS增强模式（快速+完整）
- ✅ 视频API使用正确的路径

**需要帮助？** 查看文档或运行测试脚本进行调试。

---

**祝你爬虫愉快！** 🚀





