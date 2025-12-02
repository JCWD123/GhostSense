# Motor 数据库布尔值测试错误修复

## 🐛 问题描述

访问 http://localhost:8888/api/v1/tasks 时返回 500 错误，错误消息为：

```
Database object do not implement truth value testing or bool(). 
Please compare with None instead: database is not None
```

## 🔍 问题原因

Motor (MongoDB 异步驱动) 使用了代理模式，其 `AsyncIOMotorDatabase` 对象不支持直接的布尔值测试。

**错误写法：**
```python
if not database:  # ❌ 错误
    raise RuntimeError("数据库未连接")
```

**正确写法：**
```python
if database is None:  # ✅ 正确
    raise RuntimeError("数据库未连接")
```

## 📝 修复内容

### 1. backend/core/database.py

**第 83 行：**
```python
# 修复前
if not self.db:
    raise RuntimeError("数据库未连接")

# 修复后
if self.db is None:
    raise RuntimeError("数据库未连接")
```

**第 104 行：**
```python
# 修复前
if not mongo_db.db:
    raise RuntimeError("数据库未连接")

# 修复后
if mongo_db.db is None:
    raise RuntimeError("数据库未连接")
```

### 2. backend/core/cache.py

**第 153 行：**
```python
# 修复前
if not redis_cache.redis:
    raise RuntimeError("Redis 未连接")

# 修复后
if redis_cache.redis is None:
    raise RuntimeError("Redis 未连接")
```

## ✅ 测试步骤

### 1. 重启后端服务
```bash
# 先停止后端（Ctrl+C）
cd backend
python main.py
```

### 2. 测试 API
```bash
# 健康检查
curl http://localhost:8888/health

# 获取任务列表（之前返回 500，现在应该返回 200）
curl http://localhost:8888/api/v1/tasks

# 或使用测试脚本
.\test_api.ps1  # Windows
./test_api.sh   # Linux/Mac
```

### 3. 测试前端
1. 刷新 Electron 应用（或重启）
2. 打开任务管理页面
3. 应该能正常加载任务列表（不再显示错误提示）
4. Dashboard 页面的统计数据应该正常显示

## 📚 相关知识

### Motor 的代理模式

Motor 使用代理模式实现异步访问，其对象不支持以下操作：
- ❌ 布尔值测试：`if database:` 或 `if not database:`
- ❌ `bool()` 函数：`bool(database)`
- ✅ None 比较：`if database is None:` 或 `if database is not None:`

### 最佳实践

在使用 Motor 或类似异步库时，始终使用显式的 `is None` 检查：

```python
# ✅ 推荐写法
if obj is None:
    # 对象未初始化
    pass

if obj is not None:
    # 对象已初始化
    pass

# ❌ 避免使用
if not obj:  # 可能抛出异常
    pass

if obj:  # 可能抛出异常
    pass
```

## 🎯 预期结果

修复后：
- ✅ API `/api/v1/tasks` 返回 200 状态码
- ✅ 前端任务列表正常加载
- ✅ Dashboard 统计数据正常显示
- ✅ 不再出现 "Database object do not implement..." 错误

## 📖 参考资料

- [Motor 官方文档](https://motor.readthedocs.io/)
- [Motor GitHub Issue - Truth Value Testing](https://github.com/mongodb/motor/issues/139)


