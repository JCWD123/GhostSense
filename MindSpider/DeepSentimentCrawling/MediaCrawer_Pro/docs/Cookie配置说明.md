# 小红书 Cookie 配置说明

## 🔐 为什么需要 Cookie？

根据测试结果：
```
{'code': -101, 'success': False, 'msg': '无登录信息，或登录信息为空'}
```

小红书的某些 API（特别是评论接口）需要登录状态才能访问。

---

## 📋 获取 Cookie 的方法

### 方法 1: 使用浏览器开发者工具（推荐）

1. **打开小红书网页**
   ```
   https://www.xiaohongshu.com
   ```

2. **登录你的账号**

3. **打开开发者工具**
   - Windows: `F12` 或 `Ctrl+Shift+I`
   - Mac: `Cmd+Option+I`

4. **进入 Network 标签页**
   - 刷新页面（F5）
   - 找到任意请求
   - 点击查看 Headers
   - 复制 Cookie 值

5. **需要的关键 Cookie**
   ```
   a1=xxx
   web_session=xxx
   webId=xxx
   websectiga=xxx
   ```

---

## 🔧 配置 Cookie 到系统

### 方法 1: 通过前端界面添加账号

1. 打开 Electron 应用或 http://localhost:5173
2. 进入 "账号管理"
3. 点击 "添加账号"
4. 填写信息：
   ```json
   {
     "platform": "xhs",
     "username": "你的昵称",
     "cookies": {
       "a1": "xxx",
       "web_session": "xxx",
       "webId": "xxx"
     }
   }
   ```

### 方法 2: 直接插入数据库

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def add_account():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["mediacrawler_pro"]
    
    account = {
        "platform": "xhs",
        "username": "测试账号",
        "status": "active",
        "cookies": {
            "a1": "你的a1值",
            "web_session": "你的web_session值",
            "webId": "你的webId值"
        },
        "created_at": "2025-11-17T00:00:00"
    }
    
    await db.accounts.insert_one(account)
    print("✅ 账号添加成功")
    client.close()

asyncio.run(add_account())
```

### 方法 3: 使用 API 添加

```bash
curl -X POST http://localhost:8888/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "username": "测试账号",
    "cookies": {
      "a1": "你的a1值",
      "web_session": "你的web_session值",
      "webId": "你的webId值"
    }
  }'
```

---

## 🧪 测试 Cookie 是否有效

创建测试脚本 `test_cookie.py`:

```python
import sys
sys.path.insert(0, 'backend')

import asyncio
from crawler.xhs_client import XHSClient

async def test():
    async with XHSClient() as client:
        # 设置 Cookie
        cookie_str = "a1=你的值; web_session=你的值; webId=你的值"
        client.set_cookie(cookie_str)
        
        # 测试搜索
        notes = await client.search_notes("Python", page=1, page_size=5)
        if notes:
            print(f"✅ 成功搜索到 {len(notes)} 条笔记")
            for note in notes:
                print(f"  - {note['title']}")
        else:
            print("❌ 搜索失败")

asyncio.run(test())
```

---

## ⚠️ 重要提示

### Cookie 有效期

- Cookie 通常有有效期限制
- 如果失效需要重新获取
- 建议定期更新

### 账号安全

- 不要分享你的 Cookie
- Cookie 相当于登录凭证
- 建议使用小号测试

### 反爬限制

即使有 Cookie，也可能遇到：
- 请求频率限制
- IP 限制
- 需要验证码

**解决方案：**
1. 降低请求频率（已在代码中添加延时）
2. 使用代理 IP 轮换
3. 配置多个账号轮换使用

---

## 🎯 当前系统支持

✅ **不需要 Playwright**
- 纯 HTTP 请求
- 签名服务提供 x-s、x-t
- 设置 Cookie 后即可访问

✅ **签名算法已实现**
- 签名服务在运行（端口 3000）
- 自动为每个请求生成签名
- 无需手动处理

✅ **已支持的功能**
- 搜索笔记
- 获取笔记详情
- 获取评论
- 获取推荐流
- 获取视频链接

❌ **不需要的功能**
- Playwright 自动化
- 浏览器环境
- 人工验证码处理

---

## 📊 配置 Cookie 后的效果

**配置前：**
```
搜索接口：404 错误（URL拼写错误）
评论接口：-101 无登录信息
数据：0 条笔记，0 条评论
```

**配置后：**
```
搜索接口：✅ 返回笔记列表
评论接口：✅ 返回评论数据
数据：✅ 保存到数据库
```

---

## 🚀 下一步

1. **修复 URL 拼写错误**（我已修复）
2. **配置一个小红书账号的 Cookie**
3. **重新测试 API**
4. **启动任务爬取数据**

---

需要帮助获取 Cookie 吗？我可以提供更详细的步骤！









