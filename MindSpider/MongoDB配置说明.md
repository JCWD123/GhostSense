# MongoDB 配置说明

## 概述

MindSpider项目的MediaCrawler模块现已支持MongoDB数据库存储。本文档说明如何配置和使用MongoDB。

## 环境变量配置

在项目根目录或MindSpider目录下创建`.env`文件，添加以下MongoDB配置：

### 方式1：使用MongoDB URI（推荐用于云服务）

```bash
# MongoDB URI连接字符串
MONGODB_URI=mongodb://username:password@host:port/database

# 示例（阿里云MongoDB）
MONGODB_URI=mongodb://root:MyPassword123@dds-xxx.mongodb.rds.aliyuncs.com:3717/bettafish
```

### 方式2：使用分开的配置（推荐用于本地MongoDB）

```bash
# MongoDB 主机地址
MONGODB_DB_HOST=localhost

# MongoDB 端口
MONGODB_DB_PORT=27017

# MongoDB 用户名（无认证时留空）
MONGODB_DB_USER=

# MongoDB 密码（无认证时留空）
MONGODB_DB_PWD=

# MongoDB 数据库名称
MONGODB_DB_NAME=bettafish
```

## 使用方法

### 1. 安装依赖

确保已安装motor驱动：

```bash
cd MindSpider/DeepSentimentCrawling/MediaCrawler
pip install -r requirements.txt
```

### 2. 运行爬虫并使用MongoDB存储

在MindSpider目录下运行：

```bash
# 爬取知乎平台数据并存储到MongoDB
python main.py --deep-sentiment --platforms zhihu --save-data-option mongodb

# 爬取多个平台
python main.py --deep-sentiment --platforms zhihu bili xhs --save-data-option mongodb

# 完整工作流程（话题提取 + 情感爬取）
python main.py --complete --platforms zhihu --save-data-option mongodb
```

### 3. 数据存储结构

MongoDB中的数据按平台和类型组织：

```
数据库: bettafish
├── zhihu_contents      # 知乎内容
├── zhihu_comments      # 知乎评论
├── zhihu_creators      # 知乎创作者
├── xhs_contents        # 小红书内容
├── xhs_comments        # 小红书评论
├── xhs_creators        # 小红书创作者
├── bilibili_contents   # B站内容
├── bilibili_comments   # B站评论
├── bilibili_creators   # B站创作者
└── ...                 # 其他平台
```

## 支持的平台

所有MediaCrawler支持的平台都已支持MongoDB存储：

- 小红书 (xhs)
- 抖音 (dy)
- 快手 (ks)
- B站 (bili)
- 微博 (wb)
- 百度贴吧 (tieba)
- 知乎 (zhihu)

## 数据存储选项

MediaCrawler支持多种数据存储方式，可通过`--save-data-option`参数指定：

- `csv` - CSV文件
- `json` - JSON文件
- `db` - MySQL数据库
- `sqlite` - SQLite数据库
- `postgresql` - PostgreSQL数据库
- `mongodb` - MongoDB数据库（新增）

## 注意事项

1. **连接优先级**：如果同时设置了`MONGODB_URI`和单独的配置项，系统会优先使用`MONGODB_URI`。

2. **数据库名称**：默认使用`bettafish`数据库，可通过`MONGODB_DB_NAME`环境变量修改。

3. **认证**：
   - 本地MongoDB无认证时，`MONGODB_DB_USER`和`MONGODB_DB_PWD`留空即可
   - 云服务MongoDB通常需要认证，建议使用URI方式配置

4. **网络连接**：确保MongoDB服务可访问，云服务需要配置白名单。

## 示例：完整配置文件

创建`.env`文件（参考`.env.example`）：

```bash
# ===== 数据库配置 =====
DB_DIALECT=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=mindspider
DB_CHARSET=utf8mb4

# ===== MongoDB 配置 =====
# 使用本地MongoDB（无认证）
MONGODB_DB_HOST=localhost
MONGODB_DB_PORT=27017
MONGODB_DB_USER=
MONGODB_DB_PWD=
MONGODB_DB_NAME=bettafish

# 或使用云MongoDB（有认证）
# MONGODB_URI=mongodb://username:password@host:port/bettafish

# ===== AI API 配置 =====
MINDSPIDER_API_KEY=sk-xxx
MINDSPIDER_BASE_URL=https://api.deepseek.com
MINDSPIDER_MODEL_NAME=deepseek-chat
```

## 故障排除

### 连接失败

```
[MongoDBConnection] Connection failed: ...
```

**解决方案**：
1. 检查MongoDB服务是否启动
2. 验证连接配置是否正确
3. 检查网络连接和防火墙设置
4. 云服务检查白名单配置

### 认证失败

```
Authentication failed
```

**解决方案**：
1. 确认用户名和密码正确
2. 检查用户是否有目标数据库的读写权限
3. URI格式是否正确（特殊字符需要URL编码）

## 技术实现

MongoDB存储基于以下技术：

- **motor**: 异步MongoDB驱动
- **AsyncIOMotorClient**: 异步客户端
- **单例模式**: 连接管理
- **Upsert操作**: 自动插入或更新

详细实现请参考：
- `MediaCrawler/database/mongodb_store_base.py` - MongoDB基础存储类
- `MediaCrawler/store/*/store_impl.py` - 各平台MongoDB存储实现

## 更多信息

- [MediaCrawler_new MongoDB配置总结](../DeepSentimentCrawling/MediaCrawler_new/MongoDB配置总结.md)
- [MindSpider主文档](README.md)










