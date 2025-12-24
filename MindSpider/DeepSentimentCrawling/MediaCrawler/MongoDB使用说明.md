# MongoDB 使用说明

## 快速开始

### 1. 配置MongoDB连接

在项目根目录或MindSpider目录创建`.env`文件，添加MongoDB配置：

```bash
# 方式1：使用URI（推荐云服务）
MONGODB_URI=mongodb://username:password@host:port/database

# 方式2：分开配置（推荐本地）
MONGODB_DB_HOST=localhost
MONGODB_DB_PORT=27017
MONGODB_DB_USER=
MONGODB_DB_PWD=
MONGODB_DB_NAME=bettafish
```

### 2. 安装依赖

```bash
cd MindSpider/DeepSentimentCrawling/MediaCrawler
pip install -r requirements.txt
```

### 3. 运行爬虫

从MindSpider目录运行：

```bash
# 单个平台
python main.py --deep-sentiment --platforms zhihu --save-data-option mongodb

# 多个平台
python main.py --deep-sentiment --platforms zhihu bili dy --save-data-option mongodb

# 完整工作流
python main.py --complete --platforms zhihu --save-data-option mongodb
```

## 重要说明

### 数据库隔离

MongoDB配置与MySQL/PostgreSQL **完全隔离**：

- **MySQL/PostgreSQL**：用于MindSpider主系统（话题提取、关键词管理）
- **MongoDB**：仅用于MediaCrawler爬虫数据存储（当指定`--save-data-option mongodb`时）

两个数据库系统互不影响，可以同时使用。

### 数据存储选项

MediaCrawler支持多种存储方式，通过`--save-data-option`指定：

- `db` - MySQL数据库（默认）
- `postgresql` - PostgreSQL数据库
- `mongodb` - MongoDB数据库
- `csv` - CSV文件
- `json` - JSON文件
- `sqlite` - SQLite数据库

### MongoDB数据结构

```
数据库: bettafish
├── zhihu_contents      # 知乎内容
├── zhihu_comments      # 知乎评论
├── zhihu_creators      # 知乎创作者
├── bilibili_contents   # B站内容
├── bilibili_comments   # B站评论
└── ...                 # 其他平台
```

## 配置示例

### 本地MongoDB（无认证）

```bash
MONGODB_DB_HOST=localhost
MONGODB_DB_PORT=27017
MONGODB_DB_USER=
MONGODB_DB_PWD=
MONGODB_DB_NAME=bettafish
```

### 阿里云MongoDB

```bash
MONGODB_URI=mongodb://root:MyPassword@dds-xxx.mongodb.rds.aliyuncs.com:3717/bettafish
```

## 故障排除

### 连接失败

检查：
1. MongoDB服务是否启动
2. 网络连接是否正常
3. 云服务白名单配置

### 认证失败

检查：
1. 用户名密码是否正确
2. 用户权限是否足够
3. URI格式是否正确

## 更多信息

详细配置说明请参考：
- [MindSpider MongoDB配置说明](../../MongoDB配置说明.md)
- [MediaCrawler_new MongoDB配置总结](../MediaCrawler_new/MongoDB配置总结.md)










