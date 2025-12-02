# MediaCrawer Pro - 快速启动指南

## 🚀 一键启动

### Windows (PowerShell)
```powershell
# 1. 启动后端
cd backend
python main.py

# 2. 新开终端 - 启动前端 + Electron
cd frontend
npm run electron:dev
```

### Linux/Mac
```bash
# 1. 启动后端
cd backend
python main.py

# 2. 新开终端 - 启动前端 + Electron
cd frontend
npm run electron:dev
```

---

## ✨ 新功能

### 1. API 文档 📖
```
启动后端后访问: http://localhost:8888/docs
```
美观的 API 文档页面，包含所有接口说明。

### 2. 前端 API 集成 🔌
前端已完全集成后端 API：
- ✅ 任务管理（创建、查询、删除）
- ✅ 账号管理
- ✅ 代理管理
- ✅ 健康检查
- ✅ 自动错误处理

### 3. Electron 远程调试 🔍
开发模式下自动启用远程调试（端口 9222）：

**使用 Chrome 调试：**
1. 打开 Chrome 浏览器
2. 访问 `chrome://inspect/#devices`
3. 找到 MediaCrawer Pro 应用
4. 点击 "inspect" 开始调试

**调试功能：**
- 查看 DOM 元素
- 调试 JavaScript 代码
- 查看网络请求
- 查看 Console 日志

---

## 📋 验证清单

### 后端服务
```bash
# 健康检查
curl http://localhost:8888/health

# 查看 API 文档
浏览器打开: http://localhost:8888/docs
```

### 前端应用
- [ ] Dashboard 显示"后端服务：正常"
- [ ] 可以在任务页面创建任务
- [ ] API 错误时显示友好提示

### Electron 调试
- [ ] 控制台显示"远程调试已启用，端口: 9222"
- [ ] Chrome inspect 中可以看到应用
- [ ] 可以使用 DevTools 调试

---

## 🧪 测试 API

### 使用脚本测试（推荐）
```bash
# Windows
.\test_api.ps1

# Linux/Mac
chmod +x test_api.sh
./test_api.sh
```

### 手动测试
```bash
# 1. 健康检查
curl http://localhost:8888/health

# 2. 创建任务
curl -X POST http://localhost:8888/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"platform":"xhs","type":"search","keywords":["测试"],"max_count":10}'

# 3. 获取任务列表
curl http://localhost:8888/api/v1/tasks
```

---

## 🔧 配置

### 后端配置
编辑 `backend/core/config.py`

### 前端 API 地址
编辑 `frontend/src/api/config.ts`
```typescript
export const API_BASE_URL = 'http://localhost:8888'
```

---

## 📚 详细文档

查看详细说明：[问题修复说明.md](docs/问题修复说明.md)

---

## ❓ 常见问题

**Q: 前端显示"无法连接到服务器"？**  
A: 确保后端服务已启动（`python backend/main.py`）

**Q: Electron 窗口是空白的？**  
A: 等待 Vite 开发服务器启动（端口 5173），或检查控制台错误

**Q: API 调用返回 404？**  
A: 检查后端日志，确保所有路由已正确注册

---

## 🎯 下一步

1. 查看 [API 文档](http://localhost:8888/docs)
2. 在前端创建第一个任务
3. 使用 Chrome DevTools 调试前端
4. 阅读完整文档了解更多功能

---

**享受 MediaCrawer Pro！** 🎉


