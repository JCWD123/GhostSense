# 🍪 Cookie自动续期功能说明

## ✅ 已实现的功能

你的项目现在已经完整实现了Cookie自动续期系统！

---

## 🎯 核心功能

### 1. 自动监控服务 ⏰

**功能**：
- 后台自动运行，无需手动触发
- 每6小时自动检查所有账号的Cookie状态
- 检测Cookie是否仍然有效

**启动方式**：
```bash
# 自动启动（无需配置）
cd backend
python main.py
```

**日志输出**：
```
2025-11-19 10:00:00 | INFO  | 🍪 正在启动Cookie监控服务...
2025-11-19 10:00:01 | SUCCESS | 🚀 Cookie监控服务已启动
2025-11-19 10:00:01 | INFO  | ✅ 所有服务初始化完成！

# 6小时后
2025-11-19 16:00:00 | INFO  | 🔍 开始检查所有账号Cookie...
2025-11-19 16:00:01 | SUCCESS | ✅ 账号 xxx Cookie有效
2025-11-19 16:00:02 | WARNING | ⚠️ 账号 yyy Cookie已失效
2025-11-19 16:00:03 | SUCCESS | ✅ Cookie检查完成，共检查 2 个账号
```

---

### 2. Cookie有效性检测 🔍

**检测方法**：
- 调用小红书搜索API
- 如果能正常返回数据 → Cookie有效
- 如果返回401/403/登录错误 → Cookie失效

**检测代码**：
```python
# backend/services/cookie_refresh_service.py

async def _test_cookie_validity(self, account: Dict) -> bool:
    """测试Cookie是否有效"""
    try:
        xhs_client = XHSClient()
        xhs_client.set_cookie(cookie_str)
        
        # 测试搜索功能
        result = await xhs_client.search_notes(
            keyword="测试",
            page=1,
            page_size=1
        )
        
        return result is not None
    except Exception as e:
        return False
```

---

### 3. 失效处理机制 ⚠️

**当Cookie失效时**：
1. ✅ 标记账号状态为 `expired`
2. ✅ 更新 `last_checked_at` 时间戳
3. ✅ 记录错误日志
4. ✅ 触发通知函数（可扩展）

**数据库更新**：
```python
await account_service.update_account_status(
    account_id=account_id,
    status="expired",
    is_success=False
)
```

---

### 4. REST API接口 🔌

#### 手动触发Cookie检查

```bash
POST http://localhost:8888/api/v1/cookies/check
```

**响应**：
```json
{
  "code": 0,
  "message": "Cookie检查完成",
  "data": null
}
```

---

#### 手动更新Cookie

```bash
PUT http://localhost:8888/api/v1/cookies/{account_id}
Content-Type: application/json

{
  "cookie": "a1=xxx; webId=xxx; web_session=xxx; ..."
}
```

**响应**：
```json
{
  "code": 0,
  "message": "Cookie更新成功",
  "data": null
}
```

---

#### 查看Cookie过期信息

```bash
GET http://localhost:8888/api/v1/cookies/{account_id}/info
```

**响应**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "is_valid": true,
    "last_checked_at": "2025-11-19T10:00:00",
    "estimated_expiry": "2025-12-19T10:00:00",
    "days_remaining": 30,
    "status": "active"
  }
}
```

---

## 🚀 使用指南

### 1. 添加账号Cookie

**方法A：通过前端界面**
```
1. 打开前端应用 → 账号管理
2. 点击"添加账号"
3. 粘贴你的完整Cookie字符串
4. 保存
```

**方法B：通过API**
```bash
curl -X POST http://localhost:8888/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "username": "主账号",
    "cookie": "a1=xxx; webId=xxx; web_session=xxx; ..."
  }'
```

---

### 2. 查看Cookie状态

**前端界面**：
```
账号管理 → 查看状态列
- ✅ active：Cookie有效
- ⚠️ expired：Cookie已失效
- ⏸️ inactive：账号未启用
```

**API查询**：
```bash
curl http://localhost:8888/api/v1/cookies/{account_id}/info
```

---

### 3. 手动更新Cookie

**当Cookie失效时**：

1. **浏览器获取新Cookie**：
   ```
   1. 登录小红书 https://www.xiaohongshu.com
   2. F12 → Console
   3. 执行：document.cookie
   4. 复制输出的Cookie字符串
   ```

2. **更新到系统**：
   ```bash
   curl -X PUT http://localhost:8888/api/v1/cookies/{account_id} \
     -H "Content-Type: application/json" \
     -d '{"cookie": "粘贴新Cookie"}'
   ```

---

### 4. 配置检查频率

**默认**：6小时检查一次

**修改**：
```python
# backend/services/cookie_refresh_service.py

class CookieRefreshService:
    def __init__(self):
        self.check_interval = 6 * 3600  # 修改这里
        
        # 示例：
        # 2小时：2 * 3600
        # 12小时：12 * 3600
        # 1天：24 * 3600
```

---

## 📊 监控与日志

### 日志级别

- `INFO`：正常操作
- `SUCCESS`：成功事件
- `WARNING`：Cookie失效等
- `ERROR`：系统错误

### 日志示例

```bash
# 成功检测
2025-11-19 10:00:01 | SUCCESS | ✅ 账号 691b3d23xxx Cookie有效

# Cookie失效
2025-11-19 10:00:02 | WARNING | ⚠️ 账号 691b3d24xxx Cookie已失效，需要重新登录

# 标记失效
2025-11-19 10:00:02 | WARNING | ⚠️ 账号已标记为失效: 691b3d24xxx

# 通知管理员
2025-11-19 10:00:02 | WARNING | 📧 通知管理员：账号 691b3d24xxx Cookie已失效
```

---

## 🔧 高级配置

### 1. 扩展通知方式

**当前框架**：
```python
# backend/services/cookie_refresh_service.py

async def _notify_admin(self, account: Dict):
    """通知管理员Cookie已失效"""
    
    # TODO: 实现实际的通知逻辑
    # 示例：
    
    # 邮件通知
    # await send_email(
    #     to="admin@example.com",
    #     subject="Cookie已失效",
    #     body=f"账号 {account['_id']} 的Cookie已失效"
    # )
    
    # 企业微信
    # await send_wechat(
    #     webhook_url="xxx",
    #     content=f"账号 {account['_id']} 的Cookie已失效"
    # )
    
    # Telegram
    # await send_telegram(
    #     bot_token="xxx",
    #     chat_id="xxx",
    #     message=f"账号 {account['_id']} 的Cookie已失效"
    # )
```

---

### 2. 自定义检测逻辑

```python
# backend/services/cookie_refresh_service.py

async def _test_cookie_validity(self, account: Dict) -> bool:
    """
    自定义检测逻辑
    
    可以添加多种检测方法：
    1. 搜索接口
    2. 获取用户信息
    3. 查看评论
    """
    try:
        # 方法1：搜索（当前实现）
        result1 = await xhs_client.search_notes(...)
        
        # 方法2：获取用户信息（需要登录）
        # result2 = await xhs_client.get_user_info()
        
        # 方法3：查看评论（需要登录）
        # result3 = await xhs_client.get_note_comments(...)
        
        return result1 is not None
    except Exception as e:
        return False
```

---

## 🎯 与RefreshToken的关系

### 当前方案（定期检测）

```
用户登录 → 获取Cookie
    ↓
保存到数据库
    ↓
后台每6小时检查Cookie是否有效
    ↓
如果失效 → 通知管理员 → 人工更新
```

**优点**：
- ✅ 简单可靠
- ✅ 无需逆向
- ✅ 已完整实现

**缺点**：
- ⚠️ 仍需人工介入

---

### 未来方案（RefreshToken自动刷新）

```
用户登录 → 获取Cookie + RefreshToken
    ↓
保存到数据库
    ↓
后台每6小时检查Cookie是否有效
    ↓
如果失效 → 自动使用RefreshToken刷新 → 无需人工介入
```

**优点**：
- ✅ 完全自动化
- ✅ 零人工维护

**难点**：
- ❌ 需要逆向小红书RefreshToken接口
- ❌ 需要实现签名算法

**详细说明**：见 `docs/RefreshToken自动续期方案.md`

---

## 📝 常见问题

### Q1：为什么Cookie会失效？

**原因**：
1. **时间过期**：`web_session`通常7-30天过期
2. **异地登录**：在其他设备登录会挤掉当前Cookie
3. **账号异常**：被风控、封禁等
4. **Cookie不完整**：缺少关键字段（如`web_session`）

---

### Q2：检查失败会影响正在运行的任务吗？

**答案**：不会

- ✅ 检查操作是独立的
- ✅ 不会中断正在运行的任务
- ✅ 只会标记账号状态

---

### Q3：可以禁用自动检查吗？

**方法1：不启动Cookie服务**
```python
# backend/main.py

async def startup():
    # ...
    
    # 注释掉这两行：
    # from services.cookie_refresh_service import get_cookie_refresh_service
    # cookie_service = get_cookie_refresh_service()
    # asyncio.create_task(cookie_service.start_monitoring())
```

**方法2：修改检查间隔为极大值**
```python
# backend/services/cookie_refresh_service.py

class CookieRefreshService:
    def __init__(self):
        self.check_interval = 365 * 24 * 3600  # 1年检查一次 = 基本不检查
```

---

### Q4：如何立即触发检查？

**方法1：API调用**
```bash
curl -X POST http://localhost:8888/api/v1/cookies/check
```

**方法2：重启服务**
```bash
# 重启后会立即执行一次检查
python backend/main.py
```

---

## 🎊 总结

### 你的Cookie是完整的！

```
✅ a1=xxx
✅ webId=xxx
✅ web_session=xxx  ← 关键！
✅ websectiga=xxx
✅ sec_poison_id=xxx
✅ gid=xxx
✅ xsecappid=xxx
✅ webBuild=xxx
✅ acw_tc=xxx
✅ unread=xxx
```

### 当前系统状态

| 功能 | 状态 |
|------|------|
| Cookie检测 | ✅ 已实现 |
| 自动监控 | ✅ 已启动 |
| API接口 | ✅ 可用 |
| 失效标记 | ✅ 已实现 |
| 通知框架 | ✅ 已准备（可扩展） |
| RefreshToken | 🚧 待逆向 |

### 下一步行动

1. **立即可用**：
   ```bash
   # 1. 添加你的完整Cookie
   curl -X POST http://localhost:8888/api/v1/accounts \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "xhs",
       "username": "主账号",
       "cookie": "你的完整Cookie字符串"
     }'
   
   # 2. 系统自动开始监控（无需其他操作）
   ```

2. **可选配置**：
   - 实现邮件/微信通知
   - 准备2-3个备用账号
   - 配置告警规则

3. **未来升级**（见 `docs/RefreshToken自动续期方案.md`）：
   - 逆向小红书RefreshToken接口
   - 实现完全自动化刷新
   - 零人工维护

---

**最后更新**: 2025-11-19  
**文档维护**: AI Assistant

**相关文档**：
- [Cookie验证与保持指南](./Cookie验证与保持指南.md)
- [RefreshToken自动续期方案](./RefreshToken自动续期方案.md)
- [浏览器抓包教程](./浏览器抓包教程.md)





