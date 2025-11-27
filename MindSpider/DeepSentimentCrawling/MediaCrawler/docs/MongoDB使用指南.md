# MongoDB 存储集成指南

## 📋 目录

- [简介](#简介)
- [安装依赖](#安装依赖)
- [MongoDB 部署](#mongodb-部署)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [数据结构](#数据结构)
- [性能优化](#性能优化)
- [常见问题](#常见问题)

---

## 🎯 简介

BettaFish 现已支持 MongoDB 作为数据存储方案！MongoDB 是一个高性能的 NoSQL 文档数据库，非常适合社交媒体数据的存储和分析。

### ✨ MongoDB 优势

- ✅ **灵活的 Schema**：无需预定义表结构
- ✅ **高性能写入**：支持高并发插入
- ✅ **水平扩展**：分片集群支持 PB 级数据
- ✅ **嵌套文档**：天然支持 JSON 格式
- ✅ **强大查询**：聚合管道支持复杂分析

---

## 📦 安装依赖

### 方法一：使用 pip 安装

```bash
# 安装 MongoDB 异步驱动
pip install motor==3.3.2
```

### 方法二：使用项目提供的 requirements

```bash
# 安装 MongoDB 相关依赖
pip install -r requirements-mongodb.txt
```

---

## 🐳 MongoDB 部署

### 方式一：Docker 快速部署（推荐）

```bash
# 1. 启动单机 MongoDB
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=your_password \
  -v mongodb_data:/data/db \
  mongo:7.0

# 2. 创建应用数据库和用户
docker exec -it mongodb mongosh -u admin -p your_password --authenticationDatabase admin

> use bettafish
> db.createUser({
    user: "bettafish",
    pwd: "your_app_password",
    roles: [{role: "readWrite", db: "bettafish"}]
  })
```

### 方式二：Docker Compose 部署

创建 `docker-compose-mongodb.yml`：

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: bettafish_mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: your_root_password
      MONGO_INITDB_DATABASE: bettafish
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    networks:
      - bettafish_network

volumes:
  mongodb_data:
  mongodb_config:

networks:
  bettafish_network:
    driver: bridge
```

启动：

```bash
docker-compose -f docker-compose-mongodb.yml up -d
```

### 方式三：本地安装

参考 MongoDB 官方文档：https://www.mongodb.com/docs/manual/installation/

---

## ⚙️ 配置说明

### 1. 环境变量配置（推荐）

创建或编辑 `.env` 文件：

```bash
# MongoDB 配置
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=bettafish
MONGODB_PASSWORD=your_app_password
MONGODB_DB_NAME=bettafish
MONGODB_AUTH_SOURCE=admin
```

### 2. 代码配置

编辑 `config/base_config.py`：

```python
# 数据保存类型
SAVE_DATA_OPTION = "mongodb"
```

---

## 🚀 使用方法

### 1. 初始化 MongoDB

```bash
# 初始化 MongoDB（创建索引）
python main.py --init_db mongodb

# 或使用 uv
uv run main.py --init_db mongodb
```

**输出示例：**

```
[MongoDB] Connecting to localhost:27017
[MongoDB] Connected successfully
[MongoDB] Using database: bettafish
[MongoDB] Initializing indexes...
[MongoDB] Indexes created successfully
```

### 2. 使用 MongoDB 存储数据

```bash
# 小红书关键词搜索 + MongoDB 存储
python main.py --platform xhs --lt qrcode --type search --save_data_option mongodb

# 抖音爬取 + MongoDB 存储
python main.py --platform dy --lt qrcode --type search --save_data_option mongodb

# B站爬取 + MongoDB 存储
python main.py --platform bili --lt qrcode --type search --save_data_option mongodb
```

### 3. 查看 MongoDB 数据

```bash
# 进入 MongoDB Shell
mongosh mongodb://bettafish:your_password@localhost:27017/bettafish?authSource=admin

# 查看集合
> show collections
xhs_notes
xhs_comments
xhs_creators
douyin_aweme
douyin_comments
...

# 查询笔记
> db.xhs_notes.find().limit(5).pretty()

# 统计数量
> db.xhs_notes.countDocuments()
```

---

## 📊 数据结构

### 小红书笔记（xhs_notes）

```javascript
{
    "_id": ObjectId("..."),
    "note_id": "abc123",
    "type": "normal",  // or "video"
    "title": "美食推荐",
    "desc": "今天吃了很好吃的火锅...",
    "video_url": "https://...",
    "note_url": "https://www.xiaohongshu.com/explore/...",
    "source_keyword": "美食",
    "xsec_token": "...",
    
    // 用户信息（嵌套文档）
    "user": {
        "user_id": "user123",
        "nickname": "美食博主",
        "avatar": "https://..."
    },
    
    // 互动数据（嵌套文档）
    "interact": {
        "liked_count": 1000,
        "collected_count": 500,
        "comment_count": 200,
        "share_count": 50
    },
    
    // 内容数据（数组）
    "images": [
        "https://img1.jpg",
        "https://img2.jpg"
    ],
    "tags": ["美食", "探店", "火锅"],
    
    "ip_location": "北京",
    
    // 时间戳
    "time": 1700000000000,
    "last_update_time": 1700000000000,
    "add_ts": 1700000000000,
    "last_modify_ts": 1700000000000,
    
    // MongoDB 特有字段
    "created_at": ISODate("2024-11-24T10:00:00Z"),
    "updated_at": ISODate("2024-11-24T10:05:00Z")
}
```

### 小红书评论（xhs_comments）

```javascript
{
    "_id": ObjectId("..."),
    "comment_id": "comment123",
    "note_id": "abc123",
    "content": "看起来好好吃！",
    "pictures": ["https://pic1.jpg"],
    
    // 用户信息
    "user": {
        "user_id": "user456",
        "nickname": "吃货小王",
        "avatar": "https://..."
    },
    
    "sub_comment_count": 5,
    "like_count": 100,
    "parent_comment_id": null,  // 二级评论时有值
    "ip_location": "上海",
    
    "create_time": 1700000000000,
    "add_ts": 1700000000000,
    "last_modify_ts": 1700000000000,
    
    "created_at": ISODate("2024-11-24T10:00:00Z"),
    "updated_at": ISODate("2024-11-24T10:05:00Z")
}
```

---

## 🔍 常用查询示例

### 1. 查找热门笔记

```javascript
// 查找点赞数最多的笔记
db.xhs_notes.find().sort({"interact.liked_count": -1}).limit(10)

// 查找最近24小时的热门笔记
db.xhs_notes.find({
    "created_at": {$gte: new Date(Date.now() - 24*60*60*1000)}
}).sort({"interact.liked_count": -1}).limit(20)
```

### 2. 聚合分析

```javascript
// 统计各标签的笔记数量
db.xhs_notes.aggregate([
    {$unwind: "$tags"},
    {$group: {
        _id: "$tags",
        count: {$sum: 1},
        avg_likes: {$avg: "$interact.liked_count"}
    }},
    {$sort: {count: -1}},
    {$limit: 10}
])

// 统计用户发布笔记数
db.xhs_notes.aggregate([
    {$group: {
        _id: "$user.user_id",
        nickname: {$first: "$user.nickname"},
        note_count: {$sum: 1},
        total_likes: {$sum: "$interact.liked_count"}
    }},
    {$sort: {note_count: -1}},
    {$limit: 20}
])
```

### 3. 全文搜索

```javascript
// 创建全文索引
db.xhs_notes.createIndex({title: "text", desc: "text"})

// 搜索包含"美食"的笔记
db.xhs_notes.find({$text: {$search: "美食"}})
```

---

## 🚀 性能优化

### 1. 索引优化

```javascript
// 查看当前索引
db.xhs_notes.getIndexes()

// 创建复合索引
db.xhs_notes.createIndex({"source_keyword": 1, "created_at": -1})
db.xhs_notes.createIndex({"user.user_id": 1, "created_at": -1})

// 创建唯一索引
db.xhs_notes.createIndex({"note_id": 1}, {unique: true})
```

### 2. 批量写入优化

MongoDB 已自动使用 `update_one` + `upsert` 实现去重和批量写入。

### 3. 连接池配置

编辑 `database/mongodb_session.py`：

```python
_mongodb_client = AsyncIOMotorClient(
    mongodb_uri,
    maxPoolSize=50,  # 最大连接数
    minPoolSize=10,  # 最小连接数
    serverSelectionTimeoutMS=5000,
)
```

---

## 🔧 常见问题

### Q1: 安装 motor 失败

```bash
# 方案1：更新 pip
pip install --upgrade pip
pip install motor

# 方案2：使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple motor
```

### Q2: 连接 MongoDB 失败

**检查清单：**

1. MongoDB 服务是否启动？
```bash
docker ps | grep mongodb
# 或
systemctl status mongod
```

2. 端口是否开放？
```bash
telnet localhost 27017
```

3. 用户名密码是否正确？
```bash
mongosh "mongodb://用户名:密码@localhost:27017/bettafish?authSource=admin"
```

### Q3: 数据写入慢

**优化建议：**

1. 检查索引是否合理
2. 增加连接池大小
3. 使用批量写入
4. 考虑使用分片集群

### Q4: 如何导出数据

```bash
# 导出为 JSON
mongoexport --uri="mongodb://用户名:密码@localhost:27017/bettafish?authSource=admin" \
  --collection=xhs_notes \
  --out=xhs_notes.json

# 导出为 CSV
mongoexport --uri="mongodb://用户名:密码@localhost:27017/bettafish?authSource=admin" \
  --collection=xhs_notes \
  --type=csv \
  --fields=note_id,title,user.nickname,interact.liked_count \
  --out=xhs_notes.csv
```

### Q5: 如何备份数据

```bash
# 备份整个数据库
mongodump --uri="mongodb://用户名:密码@localhost:27017/bettafish?authSource=admin" \
  --out=backup_$(date +%Y%m%d)

# 恢复数据库
mongorestore --uri="mongodb://用户名:密码@localhost:27017/bettafish?authSource=admin" \
  backup_20241124/
```

---

## 📈 与 PostgreSQL/MySQL 对比

| 特性 | MongoDB | PostgreSQL | MySQL |
|-----|---------|-----------|-------|
| Schema 灵活性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 写入性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 查询性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 水平扩展 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 事务支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 学习曲线 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 最佳实践

1. **开发环境**：使用 Docker 单机 MongoDB
2. **生产环境**：使用副本集或分片集群
3. **数据量 < 100GB**：单机足够
4. **数据量 > 1TB**：考虑分片集群
5. **定期备份**：使用 mongodump 定时备份
6. **监控**：使用 MongoDB Compass 或 Ops Manager

---

## 📚 参考资料

- [MongoDB 官方文档](https://www.mongodb.com/docs/)
- [Motor 文档](https://motor.readthedocs.io/)
- [PyMongo 文档](https://pymongo.readthedocs.io/)

---

## 💡 技术支持

如遇到问题，请：

1. 查看日志文件
2. 检查 MongoDB 连接
3. 参考常见问题
4. 提交 Issue

---

**BettaFish MongoDB 集成** - 让数据存储更灵活高效！ 🚀




