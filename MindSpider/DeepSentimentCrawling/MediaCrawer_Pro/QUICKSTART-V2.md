# 🚀 MediaCrawler Pro V2.0 快速开始

## 📦 全新特性

- ✅ 签名算法完全解耦，支持独立使用
- ✅ Playwright自动获取完整签名（包括x-s-common）
- ✅ Playwright驾驶Electron浏览器（轻量化）
- ✅ 混合模式：纯JS + 浏览器智能选择

---

## 🎯 10分钟快速上手

### 第1步：安装依赖

```bash
# 1. 签名服务
cd signature-service
npm install

# 2. 安装Playwright浏览器（首次使用）
npx playwright install chromium

# 3. Python后端（如有新依赖）
cd ../backend
pip install httpx
```

### 第2步：启动服务

打开3个终端窗口：

**终端1 - 签名服务：**
```bash
cd signature-service
npm start
```

看到以下输出表示成功：
```
🚀 ========================================
📦 MediaCrawler 签名服务已启动
🌐 监听地址: http://0.0.0.0:3100
🎯 版本: 2.0.0 (支持 Playwright + Electron)
========================================
```

**终端2 - Python后端：**
```bash
cd backend
python main.py
```

**终端3 - Electron前端：**
```bash
cd frontend
npm run electron:dev
```

看到以下输出表示Electron已启用调试端口：
```
🔍 远程调试已启用，端口: 9222
```

### 第3步：测试签名服务

**测试1：纯JS签名（最快）**

```bash
curl -X POST http://localhost:3100/sign/xhs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    "method": "GET",
    "data": {"keyword": "美食"},
    "a1": "your_a1_value"
  }'
```

**测试2：健康检查**

```bash
curl http://localhost:3100/health
```

**测试3：运行测试套件**

```bash
cd signature-service
npm test
```

---

## 💡 三种使用方式

### 方式1：Python后端直接使用（推荐）

```python
# 在你的Python代码中
from backend.crawler.xhs_client_v2 import XhsClientV2

async def search_notes():
    cookie = "a1=xxx; webId=xxx; web_session=xxx"
    
    async with XhsClientV2(cookie=cookie, use_electron=True) as client:
        # 自动模式：优先JS，需要时用浏览器
        result = await client.search_notes(
            keyword="美食",
            page=1,
            signature_mode="auto"  # 自动选择最优方案
        )
        
        print(f"找到 {len(result['data']['items'])} 条笔记")
        return result

# 运行
import asyncio
asyncio.run(search_notes())
```

### 方式2：HTTP API调用（跨语言）

**任何语言都可以调用：**

```python
# Python
import httpx

async def get_signature():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3100/sign/xhs/hybrid",
            json={
                "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
                "method": "GET",
                "data": {"keyword": "美食"},
                "cookie": "your_cookie",
                "mode": "auto"
            }
        )
        return response.json()
```

```javascript
// Node.js
const response = await fetch("http://localhost:3100/sign/xhs/hybrid", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        url: "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
        method: "GET",
        data: { keyword: "美食" },
        mode: "auto"
    })
});
const result = await response.json();
```

### 方式3：Node.js SDK（NPM包）

```javascript
const { HybridSignatureClient } = require('./signature-service/src/sdk/index');

async function main() {
    const client = new HybridSignatureClient({
        debugPort: 9222  // 连接Electron
    });
    
    const headers = await client.getHeaders({
        platform: 'xhs',
        url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
        method: 'GET',
        data: { keyword: '美食' },
        cookie: 'your_cookie',
        mode: 'auto'
    });
    
    console.log('签名:', headers);
    
    await client.close();
}

main();
```

---

## 🎯 三种签名模式

### 模式1：纯JS签名（⚡ 最快）

```python
result = await client.search_notes(
    keyword="美食",
    signature_mode="js"  # 纯JS逆向
)
```

**特点：**
- ⚡ 速度极快（10-50ms）
- 💚 资源占用低
- ✅ 生成 x-s, x-t
- ❌ 不包含 x-s-common

**适用场景：** 高频API调用、追求速度

### 模式2：浏览器模式（🎯 完整）

```python
result = await client.search_notes(
    keyword="美食",
    signature_mode="browser"  # Playwright浏览器
)
```

**特点：**
- 🐢 较慢（1-3秒）
- 🔴 资源占用较高
- ✅ 完整签名（x-s, x-t, x-s-common）
- ✅ 真实浏览器环境，绕过检测

**适用场景：** 需要完整签名、首次请求、复杂接口

### 模式3：自动模式（🌟 推荐）

```python
result = await client.search_notes(
    keyword="美食",
    signature_mode="auto"  # 智能选择
)
```

**特点：**
- ⚡ 通常很快（优先使用JS）
- 💚 资源占用低
- ✅ 失败自动降级到浏览器
- ✅ 根据需求智能选择

**适用场景：** 所有场景（推荐默认使用）

---

## 🔧 Electron集成配置

### 前端配置（已完成）

`frontend/electron/main.js` 已配置好调试端口：

```javascript
app.commandLine.appendSwitch('--remote-debugging-port', '9222');
app.commandLine.appendSwitch('--remote-allow-origins', '*');
```

### 后端配置

`.env` 文件添加：

```env
# 签名服务
SIGNATURE_SERVICE_URL=http://localhost:3100
SIGNATURE_MODE=auto
USE_ELECTRON_BROWSER=true
ELECTRON_DEBUG_PORT=9222
```

### 验证连接

打开浏览器访问：
```
http://localhost:9222/json/version
```

看到JSON输出表示Electron调试端口正常。

---

## 📊 性能对比

| 场景 | 旧版本 | V2.0（JS模式） | V2.0（浏览器模式） |
|------|--------|----------------|-------------------|
| 搜索笔记 | 2-3秒 | 10-50ms ⚡ | 1-2秒 |
| 获取详情 | 2-3秒 | 10-50ms ⚡ | 1-2秒 |
| 高频调用100次 | 300秒 | 5秒 ⚡ | 150秒 |
| 内存占用 | 800MB | 300MB 💚 | 400MB |

---

## 🎨 完整示例

### 示例1：搜索并下载笔记

```python
from backend.crawler.xhs_client_v2 import XhsClientV2
import asyncio

async def search_and_download():
    cookie = "a1=xxx; webId=xxx; web_session=xxx"
    
    async with XhsClientV2(cookie=cookie, use_electron=True) as client:
        # 1. 搜索笔记
        print("🔍 搜索笔记...")
        search_result = await client.search_notes(
            keyword="美食",
            page=1,
            page_size=20,
            signature_mode="auto"
        )
        
        items = search_result.get("data", {}).get("items", [])
        print(f"✅ 找到 {len(items)} 条笔记")
        
        # 2. 获取详情
        for i, item in enumerate(items[:3], 1):
            note_id = item.get("id")
            print(f"\n{i}. 获取笔记详情: {note_id}")
            
            detail = await client.get_note_detail(
                note_id=note_id,
                signature_mode="auto"
            )
            
            note = detail.get("data", {}).get("note", {})
            print(f"   标题: {note.get('title', 'N/A')}")
            print(f"   作者: {note.get('user', {}).get('nickname', 'N/A')}")
            print(f"   点赞: {note.get('interact_info', {}).get('liked_count', 0)}")

# 运行
asyncio.run(search_and_download())
```

### 示例2：用户笔记采集

```python
async def collect_user_notes():
    cookie = "your_cookie"
    user_id = "target_user_id"
    
    async with XhsClientV2(cookie=cookie, use_electron=True) as client:
        # 1. 获取用户信息
        print("👤 获取用户信息...")
        user_info = await client.get_user_info(
            user_id=user_id,
            signature_mode="js"  # 简单接口用JS
        )
        print(f"用户: {user_info['data']['user']['nickname']}")
        
        # 2. 获取用户笔记
        print("\n📝 获取用户笔记...")
        cursor = ""
        all_notes = []
        
        for page in range(1, 4):  # 获取3页
            notes = await client.get_user_notes(
                user_id=user_id,
                cursor=cursor,
                signature_mode="auto"
            )
            
            items = notes.get("data", {}).get("notes", [])
            all_notes.extend(items)
            
            cursor = notes.get("data", {}).get("cursor", "")
            print(f"第{page}页: {len(items)} 条笔记")
            
            if not cursor:
                break
        
        print(f"\n✅ 总共采集 {len(all_notes)} 条笔记")
        return all_notes

asyncio.run(collect_user_notes())
```

---

## 🐛 常见问题

### Q1: 签名服务连接失败

```
❌ 签名服务连接失败: Connection refused
```

**解决：** 确保签名服务正在运行

```bash
cd signature-service
npm start
```

### Q2: Electron调试端口不可用

```
❌ 连接Electron失败: 端口9222不可用
```

**解决：** 确保Electron应用正在运行

```bash
cd frontend
npm run electron:dev
```

然后验证：
```bash
curl http://localhost:9222/json/version
```

### Q3: Playwright浏览器未安装

```
❌ Executable doesn't exist at ...
```

**解决：** 安装Playwright浏览器

```bash
cd signature-service
npx playwright install chromium
```

### Q4: Cookie过期

```
❌ 请求失败: 401 Unauthorized
```

**解决：** 更新Cookie

1. 打开浏览器登录小红书
2. F12打开开发者工具
3. Network标签找到任意请求
4. 复制Cookie
5. 更新代码中的cookie变量

---

## 📚 进阶使用

### 自定义签名服务端口

```bash
# 启动在其他端口
PORT=4000 npm start
```

Python配置：
```python
# .env
SIGNATURE_SERVICE_URL=http://localhost:4000
```

### 使用独立的Playwright浏览器

如果不想使用Electron：

```python
async with XhsClientV2(cookie=cookie, use_electron=False) as client:
    # 会启动独立的Playwright浏览器
    result = await client.search_notes(
        keyword="美食",
        signature_mode="browser"
    )
```

### 集成到FastAPI项目

```python
from fastapi import FastAPI
from backend.crawler.xhs_client_v2 import XhsClientV2

app = FastAPI()

@app.post("/api/search")
async def search_notes(keyword: str, cookie: str):
    async with XhsClientV2(cookie=cookie) as client:
        result = await client.search_notes(
            keyword=keyword,
            signature_mode="auto"
        )
        return result
```

---

## 🎉 下一步

- 📖 阅读 [完整优化说明](docs/优化完成说明-V2.md)
- 📚 查看 [签名SDK文档](signature-service/README-SDK.md)
- 💻 运行示例代码：
  - `node signature-service/examples/node_example.js`
  - `python signature-service/examples/python_example.py`
- 🧪 运行测试：`cd signature-service && npm test`

---

**版本：** V2.0.0  
**日期：** 2025-11-19  
**祝你使用愉快！** 🚀




