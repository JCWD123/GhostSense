# Event Loop is Closed 错误修复

## 🐛 问题描述

创建任务时后端返回 500 错误：

```
RuntimeError: Event loop is closed
500 POST /api/v1/tasks (::1) 15.66ms
ERROR | services.task_service:list_tasks:135 | ❌ 获取任务列表失败: Event loop is closed
```

## 🔍 问题原因

在 `backend/services/task_service.py` 第 71 行：

```python
# ❌ 错误代码
asyncio.create_task(self._execute_task(task))
```

**问题分析：**
- Tornado 使用自己的事件循环（基于 `tornado.ioloop.IOLoop`）
- 直接使用 `asyncio.create_task()` 会尝试在不兼容的事件循环中创建任务
- 导致 "Event loop is closed" 错误

## ✅ 修复方案

### 1. 添加 Tornado IOLoop 导入

```python
import tornado.ioloop
```

### 2. 使用 Tornado 的 spawn_callback

```python
# ✅ 正确代码
tornado.ioloop.IOLoop.current().spawn_callback(self._execute_task, task)
```

**说明：**
- `IOLoop.current()` 获取当前 Tornado 事件循环
- `spawn_callback()` 在 Tornado 事件循环中异步执行回调函数
- 这是 Tornado 推荐的异步任务启动方式

## 📝 修改内容

### backend/services/task_service.py

**第 11 行（添加导入）：**
```python
import tornado.ioloop
```

**第 71-72 行（修复任务启动）：**
```python
# 修复前
asyncio.create_task(self._execute_task(task))

# 修复后
tornado.ioloop.IOLoop.current().spawn_callback(self._execute_task, task)
```

## 🚀 测试修复

### 1. 重启后端服务
```bash
# 停止当前运行的后端（Ctrl+C）
cd backend
python main.py
```

### 2. 测试创建任务

**方法 1：使用前端**
1. 刷新 Electron 应用（Ctrl+R）
2. 进入"任务管理"页面
3. 点击"创建任务"
4. 填写表单并提交
5. 应该看到"任务创建成功"提示

**方法 2：使用 cURL**
```bash
curl -X POST http://localhost:8888/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "type": "search",
    "keywords": ["测试"],
    "max_count": 10,
    "enable_comment": true,
    "enable_download": false
  }'
```

**方法 3：使用 PowerShell 脚本**
```powershell
.\test_api.ps1
```

## 📚 相关知识

### Tornado vs asyncio

| 特性 | Tornado | asyncio |
|------|---------|---------|
| 事件循环 | `tornado.ioloop.IOLoop` | `asyncio.EventLoop` |
| 创建任务 | `IOLoop.current().spawn_callback()` | `asyncio.create_task()` |
| 运行协程 | `IOLoop.current().run_sync()` | `asyncio.run()` |
| 兼容性 | Tornado 5.0+ 兼容 asyncio | Python 3.7+ |

### Tornado 异步任务最佳实践

```python
# ✅ 推荐：使用 spawn_callback
tornado.ioloop.IOLoop.current().spawn_callback(async_function, *args)

# ✅ 推荐：使用 add_callback（同步函数）
tornado.ioloop.IOLoop.current().add_callback(sync_function, *args)

# ❌ 避免：直接使用 asyncio
asyncio.create_task(coroutine)  # 在 Tornado 中会失败

# ⚠️ 注意：run_sync 会阻塞
tornado.ioloop.IOLoop.current().run_sync(coroutine)  # 阻塞直到完成
```

### spawn_callback vs add_callback

```python
# spawn_callback - 用于协程（async def）
tornado.ioloop.IOLoop.current().spawn_callback(async_task, arg1, arg2)

# add_callback - 用于普通函数（def）
tornado.ioloop.IOLoop.current().add_callback(sync_task, arg1, arg2)
```

## 🎯 预期结果

修复后：
- ✅ POST /api/v1/tasks 返回 200 状态码
- ✅ 任务成功创建并返回任务信息
- ✅ 任务在后台异步执行
- ✅ 前端显示"任务创建成功"提示
- ✅ 不再出现 "Event loop is closed" 错误

## 🔗 相关问题

### Q1: 为什么不直接使用 asyncio?
**A:** Tornado 有自己的事件循环实现，虽然现代版本（5.0+）与 asyncio 兼容，但直接使用 `asyncio.create_task()` 可能在某些情况下失败。使用 Tornado 的 API 更可靠。

### Q2: spawn_callback 和 create_task 有什么区别？
**A:** 
- `spawn_callback` 是 Tornado 特有的，在 Tornado 的事件循环中执行
- `create_task` 是 asyncio 标准库的，需要 asyncio 事件循环
- 在 Tornado 应用中应该使用 `spawn_callback`

### Q3: 任务创建后如何查看执行状态？
**A:** 
```bash
# 查看任务列表
curl http://localhost:8888/api/v1/tasks

# 查看特定任务
curl http://localhost:8888/api/v1/tasks/{task_id}
```

## 📖 参考资料

- [Tornado Documentation - Coroutines](https://www.tornadoweb.org/en/stable/guide/coroutines.html)
- [Tornado IOLoop API](https://www.tornadoweb.org/en/stable/ioloop.html)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

## 🔄 总结

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Motor Database 布尔测试 | Motor 对象不支持 `if not obj` | 使用 `if obj is None` |
| Event loop is closed | 使用了 `asyncio.create_task()` | 使用 `tornado.ioloop.IOLoop.current().spawn_callback()` |

**记住：在 Tornado 应用中，始终使用 Tornado 的事件循环 API！**


