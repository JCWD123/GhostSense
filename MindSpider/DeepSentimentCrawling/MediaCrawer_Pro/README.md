# MediaCrawer_Pro 🚀

> 全栈自媒体平台数据采集与视频下载系统 - 专业版

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-green.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 项目特色

MediaCrawer_Pro 是 MediaCrawler 的专业升级版，提供了更强大的功能和更好的用户体验：

### 🎯 核心升级

- **🔄 断点续爬** - 支持断点续传，恢复上次爬取进度
- **👥 多账号管理** - 账号池系统，自动轮换，避免封禁
- **🌐 IP代理池** - 支持多种代理源，智能切换，稳定可靠
- **⚡ 签名服务** - 独立签名服务，解耦业务逻辑，易于扩展
- **🎨 桌面UI** - Electron桌面应用，一键下载视频
- **📡 HomeFeed** - 支持多平台首页推荐流获取
- **🪶 轻量架构** - 去除 Playwright 依赖，纯 HTTP 请求

### 📦 技术栈

#### 后端
- **Python 3.10+** - 异步编程
- **Tornado** - 高性能 Web 框架
- **Httpx** - 现代化的 HTTP 客户端
- **Pydantic** - 数据验证和序列化
- **MongoDB** - 数据存储和断点续爬
- **Redis** - 缓存和任务队列

#### 前端
- **Electron** - 跨平台桌面应用
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全
- **Vite** - 极速构建工具
- **Element UI Plus** - 优雅的组件库

#### 签名服务
- **Node.js** - JavaScript 运行时
- **Fastify** - 高性能 Web 框架
- **Crypto** - 加密算法实现

## 🏗️ 项目架构

```
MediaCrawer_Pro/
├── backend/                 # 后端服务
│   ├── api/                # API 接口
│   ├── core/               # 核心业务逻辑
│   ├── crawler/            # 爬虫引擎
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   ├── utils/              # 工具函数
│   └── main.py            # 入口文件
├── frontend/               # 前端桌面应用
│   ├── src/
│   │   ├── main/          # Electron 主进程
│   │   ├── renderer/      # Vue 渲染进程
│   │   ├── components/    # 组件
│   │   └── views/         # 视图
│   └── package.json
├── signature-service/      # 签名服务
│   ├── src/
│   │   ├── platforms/     # 平台签名算法
│   │   └── server.js      # 服务入口
│   └── package.json
├── docs/                   # 文档
└── docker-compose.yml     # Docker 编排
```

## 🚀 快速开始

### 1. 环境准备

```bash
# Python 环境
conda create -n mediacrawler-pro python=3.10
conda activate mediacrawler-pro

# Node.js 环境 (推荐使用 nvm)
nvm install 18
nvm use 18
```

### 2. 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py --port 8888
```

### 3. 签名服务启动

```bash
cd signature-service
npm install
npm start
```

### 4. 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 📖 功能说明

### 1. 断点续爬

系统会自动记录每次爬取的进度，支持以下场景：
- ✅ 程序意外中断后恢复
- ✅ 手动暂停后继续
- ✅ 分批次爬取大量数据

```python
# 使用示例
crawler = XHSCrawler()
await crawler.resume_from_checkpoint()  # 从断点恢复
```

### 2. 多账号管理

支持配置多个账号，自动轮换使用：

```yaml
# config.yaml
accounts:
  xhs:
    - cookie: "xxx1"
      weight: 1
      status: active
    - cookie: "xxx2"
      weight: 2
      status: active
```

### 3. IP代理池

支持多种代理提供商：
- 快代理
- 豌豆HTTP
- 阿布云代理
- 自定义代理

```yaml
# config.yaml
proxy:
  enabled: true
  provider: "kuaidaili"
  pool_size: 10
  retry: 3
```

### 4. 签名服务

独立的签名服务，支持：
- 小红书 x-s, x-t 签名
- 抖音 X-Bogus 签名
- 快手签名
- B站 wbi 签名

```javascript
// 调用签名服务
const sign = await fetch('http://localhost:3000/sign/xhs', {
  method: 'POST',
  body: JSON.stringify({ url, data })
});
```

### 5. 桌面应用

功能包括：
- 📝 关键词搜索
- 🎬 视频批量下载
- 📊 任务进度管理
- 📁 文件管理
- ⚙️ 配置管理

### 6. HomeFeed 推荐流

支持获取各平台首页推荐内容：
- 小红书首页推荐
- 抖音推荐
- 快手推荐
- B站推荐

## 🔧 配置说明

主配置文件 `config.yaml`:

```yaml
# 基础配置
platform: "xhs"
save_data_option: "mongodb"

# 断点续爬配置
checkpoint:
  enabled: true
  save_interval: 10  # 每10条保存一次进度

# 账号池配置
accounts:
  xhs:
    - cookie: "your_cookie_here"
      weight: 1
      status: active

# 代理池配置
proxy:
  enabled: true
  provider: "kuaidaili"
  pool_size: 10
  
# 签名服务配置
signature_service:
  url: "http://localhost:3000"
  timeout: 5

# 数据库配置
mongodb:
  uri: "mongodb://localhost:27017"
  database: "mediacrawler_pro"

redis:
  host: "localhost"
  port: 6379
  db: 0
```

## 📊 支持平台

| 平台 | 搜索 | HomeFeed | 评论 | 视频下载 | 状态 |
|------|------|----------|------|----------|------|
| 小红书 | ✅ | ✅ | ✅ | ✅ | 稳定 |
| 抖音 | ✅ | ✅ | ✅ | ✅ | 稳定 |
| 快手 | ✅ | ✅ | ✅ | ✅ | 稳定 |
| B站 | ✅ | ✅ | ✅ | ✅ | 稳定 |
| 微博 | ✅ | ✅ | ✅ | ❌ | 稳定 |
| 知乎 | ✅ | ✅ | ✅ | ❌ | 稳定 |

## 🐳 Docker 部署

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📝 API 文档

后端提供 RESTful API:

```bash
# 创建爬取任务
POST /api/v1/tasks
{
  "platform": "xhs",
  "type": "search",
  "keywords": ["Python"],
  "max_count": 100
}

# 查询任务状态
GET /api/v1/tasks/{task_id}

# 下载视频
POST /api/v1/download
{
  "url": "https://...",
  "save_path": "/path/to/save"
}
```

详细 API 文档见: [docs/API.md](docs/API.md)

## 🛠️ 开发指南

### 后端开发

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/
```

### 前端开发

```bash
cd frontend
npm run dev       # 开发模式
npm run build     # 打包
npm run test      # 测试
```

### 签名服务开发

```bash
cd signature-service
npm run dev       # 开发模式
npm test          # 测试
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢原 MediaCrawler 项目提供的基础
- 感谢所有贡献者的付出

## 📮 联系方式

- 项目主页: https://github.com/your-repo/MediaCrawer_Pro
- Issues: https://github.com/your-repo/MediaCrawer_Pro/issues
- 邮箱: your-email@example.com

## ⭐ Star History

如果这个项目对您有帮助，请给我们一个 Star ⭐

---

**Made with ❤️ by MediaCrawer Team**




