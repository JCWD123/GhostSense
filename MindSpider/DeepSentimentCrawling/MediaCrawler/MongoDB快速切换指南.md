# 🚀 MongoDB 快速切换指南

## ✨ 统一配置设计

BettaFish 现在支持**统一的数据库配置参数**，你只需要修改 `DB_DIALECT` 参数即可在 MySQL、PostgreSQL 和 MongoDB 之间无缝切换！

---

## 📋 使用你现有的配置

### 你的 `.env` 文件（保持不变）

```bash
# ====================== 数据库配置 ======================

# 数据库主机，例如localhost 或 127.0.0.1
DB_HOST=localhost

# 数据库端口号，默认为3306（MySQL）或 27017（MongoDB）
DB_PORT=3306

# 数据库用户名
DB_USER=root

# 数据库密码
DB_PASSWORD=MyPassw0rd!

# 数据库名称
DB_NAME=xhs

# 数据库字符集，推荐utf8mb4，兼容emoji（仅SQL数据库使用）
DB_CHARSET=utf8mb4

# 🔥 关键参数：数据库类型 mysql | postgresql | mongodb
DB_DIALECT=mysql
```

---

## 🎯 三步切换到 MongoDB

### 步骤 1：修改 DB_DIALECT

**只需修改一个参数：**

```bash
# 从
DB_DIALECT=mysql

# 改为
DB_DIALECT=mongodb
```

### 步骤 2：调整端口（可选）

MongoDB 默认端口是 27017：

```bash
# MySQL/PostgreSQL
DB_PORT=3306

# 改为 MongoDB
DB_PORT=27017
```

### 步骤 3：初始化并使用

```bash
# 初始化 MongoDB 索引
python main.py --init_db mongodb

# 开始爬取（自动使用 MongoDB）
python main.py --platform xhs --lt qrcode --type search --save_data_option mongodb
```

---

## 📊 配置对照表

### MySQL 配置

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_CHARSET=utf8mb4
DB_DIALECT=mysql
```

**使用命令：**
```bash
python main.py --platform xhs --type search --save_data_option db
```

---

### PostgreSQL 配置

```bash
DB_HOST=localhost
DB_PORT=5432          # 👈 PostgreSQL 默认端口
DB_USER=postgres
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_CHARSET=utf8mb4
DB_DIALECT=postgresql
```

**使用命令：**
```bash
python main.py --platform xhs --type search --save_data_option postgresql
```

---

### MongoDB 配置

```bash
DB_HOST=localhost
DB_PORT=27017         # 👈 MongoDB 默认端口
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_DIALECT=mongodb    # 👈 关键改动
```

**使用命令：**
```bash
python main.py --platform xhs --type search --save_data_option mongodb
```

---

## 🔧 端口号参考

| 数据库 | 默认端口 | DB_DIALECT 值 |
|--------|---------|--------------|
| MySQL | 3306 | `mysql` |
| PostgreSQL | 5432 | `postgresql` |
| MongoDB | 27017 | `mongodb` |

---

## 💡 配置优先级

### 方式一：使用统一的 DB_* 配置（推荐）

```bash
DB_HOST=localhost
DB_PORT=27017
DB_USER=admin
DB_PASSWORD=password
DB_NAME=bettafish
DB_DIALECT=mongodb
```

BettaFish 会自动将这些配置应用到 MongoDB。

### 方式二：使用专用的 MONGODB_* 配置（可选）

如果你需要 MongoDB 使用不同的配置，可以添加专用参数：

```bash
# 通用配置（用于 MySQL/PostgreSQL）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password1
DB_NAME=xhs

# MongoDB 专用配置（优先级更高）
MONGODB_HOST=mongodb.server.com
MONGODB_PORT=27017
MONGODB_USER=mongouser
MONGODB_PASSWORD=mongopass
MONGODB_DB_NAME=bettafish_mongo
```

**配置优先级：** `MONGODB_*` > `DB_*` > 默认值

---

## 🐳 Docker 快速启动 MongoDB

### 使用你现有的配置

```bash
# 根据你的 .env 配置启动 MongoDB
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=MyPassw0rd! \
  -e MONGO_INITDB_DATABASE=xhs \
  -v mongodb_data:/data/db \
  mongo:7.0
```

### 创建数据库和用户

```bash
# 进入 MongoDB 容器
docker exec -it mongodb mongosh -u root -p MyPassw0rd! --authenticationDatabase admin

# 创建数据库和用户
> use xhs
> db.createUser({
    user: "root",
    pwd: "MyPassw0rd!",
    roles: [{role: "readWrite", db: "xhs"}]
  })
```

---

## ✅ 验证配置

### 测试 MongoDB 连接

```bash
# 运行测试脚本
python examples/test_mongodb.py
```

**预期输出：**

```
🔌 测试 MongoDB 连接...
   主机: localhost:27017
   数据库: xhs
   用户: root
✅ MongoDB 连接成功！

📊 创建 MongoDB 索引...
✅ 索引创建成功！

💾 测试数据存储...
✅ 数据存储测试成功！

🎉 所有测试通过！MongoDB 存储功能正常
```

---

## 🔄 切换流程示例

### 场景：从 MySQL 切换到 MongoDB

```bash
# 1. 当前使用 MySQL
DB_DIALECT=mysql
python main.py --platform xhs --type search --save_data_option db

# 2. 启动 MongoDB
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=MyPassw0rd! \
  mongo:7.0

# 3. 修改配置
DB_PORT=27017        # 改端口
DB_DIALECT=mongodb   # 改类型

# 4. 初始化 MongoDB
python main.py --init_db mongodb

# 5. 开始使用 MongoDB
python main.py --platform xhs --type search --save_data_option mongodb
```

---

## 📈 三种数据库对比

| 特性 | MySQL | PostgreSQL | MongoDB |
|-----|-------|-----------|---------|
| 配置难度 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 写入性能 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Schema 灵活性 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 水平扩展 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 使用门槛 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**推荐选择：**
- 小型项目：**MySQL**（配置简单）
- 数据分析：**PostgreSQL**（查询强大）
- 大规模爬取：**MongoDB**（高性能、易扩展）

---

## 🎯 常见问题

### Q1: 我需要安装额外的包吗？

**需要！** MongoDB 需要安装 `motor` 包：

```bash
pip install motor==3.3.2
```

### Q2: 三种数据库可以同时使用吗？

**可以！** 但需要用不同的配置：

```bash
# MySQL 配置
DB_HOST=localhost
DB_PORT=3306
DB_DIALECT=mysql

# MongoDB 专用配置
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### Q3: 数据库之间可以迁移吗？

**可以！** 我们提供了数据导出导入工具（计划中）。

目前可以：
1. 从 MySQL 导出为 CSV
2. 写脚本导入 MongoDB

### Q4: 端口号必须改吗？

**建议改！** 但不是必须：
- 如果 MongoDB 运行在 3306 端口（非标准），可以不改
- 标准情况下，MongoDB 使用 27017 端口

---

## 💡 最佳实践

### 开发环境配置

```bash
# .env
DB_HOST=localhost
DB_PORT=27017
DB_USER=dev
DB_PASSWORD=dev123
DB_NAME=xhs_dev
DB_DIALECT=mongodb

# 使用 Docker
docker run -d --name mongodb-dev -p 27017:27017 mongo:7.0
```

### 生产环境配置

```bash
# .env
DB_HOST=mongodb-prod.example.com
DB_PORT=27017
DB_USER=prod_user
DB_PASSWORD=strong_password_here
DB_NAME=xhs_production
DB_DIALECT=mongodb

# 使用副本集或分片集群
```

---

## 🎉 总结

✅ **统一配置设计** - 只需修改 `DB_DIALECT` 参数  
✅ **向后兼容** - 支持 `MONGODB_*` 专用配置  
✅ **简单易用** - 三步切换数据库  
✅ **灵活选择** - MySQL、PostgreSQL、MongoDB 任意切换  

**现在，修改一个参数，就能切换数据库！** 🚀

---

## 📞 需要帮助？

1. 查看详细文档：`docs/MongoDB使用指南.md`
2. 运行测试脚本：`python examples/test_mongodb.py`
3. 提交 Issue 获取支持

**祝你爬取愉快！** 😊




