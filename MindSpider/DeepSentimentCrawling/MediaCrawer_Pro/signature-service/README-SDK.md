# 📦 MediaCrawler 签名算法 SDK

一个独立、解耦的签名算法服务，支持多平台集成。

## 🌟 特性

- ✅ 完全解耦，可独立使用
- ✅ 支持纯JS逆向（x-s, x-t）
- ✅ 支持Playwright浏览器获取（x-s-common）
- ✅ 支持多平台：小红书、抖音、快手、B站
- ✅ 支持多种集成方式：HTTP API、NPM包、Python包

## 📦 三种使用方式

### 方式1：HTTP API 服务（推荐用于跨语言）

```bash
# 启动签名服务
cd signature-service
npm install
npm start  # 默认运行在 http://localhost:3100
```

**调用示例（任何语言）：**

```python
# Python
import httpx

response = httpx.post("http://localhost:3100/sign/xhs", json={
    "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    "method": "GET",
    "data": {"keyword": "美食"},
    "a1": "your_a1_cookie"
})
sign_data = response.json()["data"]
# {"x-s": "...", "x-t": "..."}
```

```javascript
// Node.js
const response = await fetch("http://localhost:3100/sign/xhs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        url: "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
        method: "GET",
        data: { keyword: "美食" },
        a1: "your_a1_cookie"
    })
});
const signData = await response.json();
```

---

### 方式2：NPM 包（Node.js 项目）

```bash
# 将 signature-service 发布为 npm 包或直接引用
npm install ./signature-service
```

```javascript
const { XhsSignature, DouyinSignature } = require('mediacrawler-signature-sdk');

// 小红书签名
const xhsSigner = new XhsSignature();
const { xs, xt } = xhsSigner.sign({
    method: "GET",
    url: "/api/sns/web/v1/search/notes",
    data: { keyword: "美食" },
    a1: "your_a1_cookie"
});

// 抖音签名
const douyinSigner = new DouyinSignature();
const { xBogus } = douyinSigner.sign({
    url: "https://www.douyin.com/aweme/v1/web/aweme/post/",
    params: { sec_user_id: "xxx" }
});
```

---

### 方式3：Python 包（FastAPI/Django/Flask 项目）

```bash
# 通过 HTTP API 调用（推荐）
pip install httpx
```

```python
from signature_sdk import SignatureClient

# 初始化客户端
client = SignatureClient(base_url="http://localhost:3100")

# 小红书签名
sign_data = await client.get_xhs_sign(
    url="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    method="GET",
    data={"keyword": "美食"},
    a1="your_a1_cookie"
)
# {"x-s": "...", "x-t": "..."}
```

---

## 🚀 新增功能：Playwright 获取 x-s-common

### 为什么需要 Playwright？

原有的纯JS逆向只能生成 `x-s` 和 `x-t`，但缺少 `x-s-common`。  
`x-s-common` 包含设备指纹、浏览器环境等复杂信息，难以完全逆向。

**解决方案：** 使用 Playwright 在真实浏览器环境中自动获取完整的请求头。

### 使用方式

```javascript
// 方式1：HTTP API
POST http://localhost:3100/sign/xhs/playwright
{
    "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    "method": "GET",
    "data": {"keyword": "美食"},
    "cookie": "a1=xxx; webId=xxx; web_session=xxx"
}

// 返回完整请求头
{
    "x-s": "...",
    "x-t": "...",
    "x-s-common": "...",
    "cookie": "..."
}
```

```python
# 方式2：Python 调用
from signature_sdk import PlaywrightSignatureClient

client = PlaywrightSignatureClient()
await client.init()  # 启动浏览器

headers = await client.get_xhs_headers(
    url="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    method="GET",
    data={"keyword": "美食"},
    cookie="a1=xxx; webId=xxx"
)
# 返回完整的请求头，包括 x-s-common

await client.close()  # 关闭浏览器
```

---

## 🔧 架构设计

```
signature-service/
├── src/
│   ├── core/                 # 核心签名算法（纯JS逆向）
│   │   ├── xhs.js           # 小红书 x-s, x-t
│   │   ├── douyin.js        # 抖音 X-Bogus
│   │   ├── kuaishou.js      # 快手签名
│   │   └── bilibili.js      # B站 wbi
│   │
│   ├── playwright/           # 浏览器自动化获取
│   │   ├── xhs_browser.js   # 小红书浏览器获取
│   │   └── common.js        # 通用浏览器工具
│   │
│   ├── api/                  # HTTP API 服务
│   │   ├── server.js        # Fastify 服务器
│   │   └── routes.js        # 路由定义
│   │
│   └── sdk/                  # SDK 导出
│       ├── index.js         # 主入口
│       └── types.d.ts       # TypeScript 类型定义
│
├── package.json             # NPM 包配置
├── README.md                # 使用文档
└── examples/                # 示例代码
    ├── node-example.js
    ├── python-example.py
    └── fastapi-example.py
```

---

## 🎯 混合模式（推荐）

同时支持纯JS逆向和Playwright浏览器获取：

```python
from signature_sdk import HybridSignatureClient

client = HybridSignatureClient()

# 优先使用纯JS逆向（快速、轻量）
headers = await client.get_headers(
    platform="xhs",
    url="...",
    method="GET",
    mode="js"  # 纯JS逆向，只返回 x-s, x-t
)

# 如果纯JS不够，切换到浏览器模式（完整但较慢）
headers = await client.get_headers(
    platform="xhs",
    url="...",
    method="GET",
    mode="browser"  # Playwright浏览器，返回完整 headers 包括 x-s-common
)

# 自动模式：先尝试JS，失败则用浏览器
headers = await client.get_headers(
    platform="xhs",
    url="...",
    method="GET",
    mode="auto"  # 自动选择
)
```

---

## 📊 性能对比

| 模式 | 速度 | 资源消耗 | 签名完整度 | 适用场景 |
|------|------|----------|-----------|----------|
| 纯JS逆向 | ⚡ 极快 (10-50ms) | 💚 低 | x-s, x-t | 高频请求、API调用 |
| Playwright | 🐢 较慢 (1-3s) | 🔴 高 | 完整（包括x-s-common） | 需要完整环境、首次请求 |
| 混合模式 | ⚡ 快 | 💚 低 | 根据需要 | 推荐，自动降级 |

---

## 🌐 集成到其他框架

### FastAPI

```python
from fastapi import FastAPI
from signature_sdk import SignatureClient

app = FastAPI()
signature_client = SignatureClient()

@app.post("/api/xhs/search")
async def search_notes(keyword: str):
    # 获取签名
    sign = await signature_client.get_xhs_sign(
        url="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
        method="GET",
        data={"keyword": keyword}
    )
    
    # 使用签名请求小红书API
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
            params={"keyword": keyword},
            headers={
                "x-s": sign["x-s"],
                "x-t": sign["x-t"]
            }
        )
        return resp.json()
```

### Django

```python
# views.py
from django.http import JsonResponse
from signature_sdk import SignatureClient
import asyncio

signature_client = SignatureClient()

async def search_notes(request):
    keyword = request.GET.get("keyword")
    
    # 获取签名
    sign = await signature_client.get_xhs_sign(
        url="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
        method="GET",
        data={"keyword": keyword}
    )
    
    return JsonResponse(sign)
```

### Express.js

```javascript
const express = require('express');
const { XhsSignature } = require('mediacrawler-signature-sdk');

const app = express();
const xhsSigner = new XhsSignature();

app.get('/api/xhs/sign', (req, res) => {
    const { url, method, data, a1 } = req.query;
    
    const sign = xhsSigner.sign({
        url,
        method,
        data: JSON.parse(data),
        a1
    });
    
    res.json(sign);
});

app.listen(3000);
```

---

## 🔐 安全建议

1. **不要公开签名服务** - 仅在内网使用
2. **添加访问控制** - 使用 API Key 或 JWT
3. **限流保护** - 防止滥用
4. **定期更新算法** - 跟踪平台变化

---

## 📝 变更日志

### v2.0.0 (2025-11-19)
- ✨ 完全解耦，支持独立部署
- ✨ 新增 Playwright 浏览器获取模式
- ✨ 新增混合模式（JS + 浏览器）
- ✨ 支持 NPM 包、Python SDK 多种集成方式
- ✨ 完善的文档和示例

### v1.0.0
- 初始版本，仅支持 HTTP API

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License






