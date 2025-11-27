# 🎯 MongoDB 统一配置说明

## ✨ 设计理念

BettaFish 项目现已支持**统一的数据库配置参数**！

你只需要修改 `.env` 文件中的 **一个参数** (`DB_DIALECT`)，即可在 MySQL、PostgreSQL 和 MongoDB 之间无缝切换，无需修改其他配置。

---

## 📋 你的现有配置（完全兼容）

```bash
# ====================== 数据库配置 ======================

# 数据库主机，例如localhost 或 127.0.0.1
DB_HOST=localhost

# 数据库端口号，默认为3306
DB_PORT=3306

# 数据库用户名
DB_USER=root

# 数据库密码
DB_PASSWORD=MyPassw0rd!

# 数据库名称
DB_NAME=xhs

# 数据库字符集，推荐utf8mb4，兼容emoji
DB_CHARSET=utf8mb4

# 🔥 数据库类型：mysql | postgresql | mongodb
DB_DIALECT=mysql
```

---

## 🚀 切换到 MongoDB（三步完成）

### 步骤 1：修改数据库类型

**只需修改这一个参数：**

```bash
DB_DIALECT=mongodb
```

### 步骤 2：调整端口号（可选）

MongoDB 默认端口是 27017：

```bash
DB_PORT=27017
```

### 步骤 3：运行初始化

```bash
# 安装 MongoDB 依赖
pip install motor==3.3.2

# 初始化 MongoDB 索引
python main.py --init_db mongodb

# 开始爬取
python main.py --platform xhs --lt qrcode --type search --save_data_option mongodb
```

**完成！** 🎉

---

## 🎨 配置优先级

### 方式一：统一配置（推荐）✅

使用通用的 `DB_*` 参数，一套配置适用所有数据库：

```bash
DB_HOST=localhost
DB_PORT=27017
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_DIALECT=mongodb
```

**优点：**
- ✅ 配置简单，只需修改 `DB_DIALECT`
- ✅ 不同数据库使用相同的配置参数
- ✅ 适合大多数场景

### 方式二：专用配置（高级）🔧

如果需要为 MongoDB 单独配置（与 MySQL 不同的主机/端口等），可以添加专用参数：

```bash
# 通用配置（用于 MySQL/PostgreSQL）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password1
DB_NAME=xhs
DB_DIALECT=mysql

# MongoDB 专用配置（会覆盖通用配置）
MONGODB_HOST=mongodb-server.com
MONGODB_PORT=27017
MONGODB_USER=mongouser
MONGODB_PASSWORD=mongopass
MONGODB_DB_NAME=bettafish
MONGODB_AUTH_SOURCE=admin
```

**配置加载顺序：**
```
MONGODB_* 专用配置 > DB_* 通用配置 > 默认值
```

**适用场景：**
- MongoDB 和 MySQL/PostgreSQL 部署在不同服务器
- 需要不同的数据库名称或认证方式
- 需要同时连接多个数据库

---

## 🔄 实际配置示例

### 示例 1：本地开发（MySQL）

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dev123
DB_NAME=xhs_dev
DB_DIALECT=mysql
```

```bash
# 启动 MySQL
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=dev123 \
  -e MYSQL_DATABASE=xhs_dev \
  mysql:8.0

# 初始化并运行
python main.py --init_db mysql
python main.py --platform xhs --type search --save_data_option db
```

---

### 示例 2：切换到 MongoDB（同一台机器）

```bash
DB_HOST=localhost
DB_PORT=27017         # 👈 只需改端口
DB_USER=root
DB_PASSWORD=dev123
DB_NAME=xhs_dev
DB_DIALECT=mongodb    # 👈 只需改类型
```

```bash
# 启动 MongoDB
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=dev123 \
  mongo:7.0

# 安装依赖
pip install motor==3.3.2

# 初始化并运行
python main.py --init_db mongodb
python main.py --platform xhs --type search --save_data_option mongodb
```

---

### 示例 3：生产环境（MongoDB 在远程服务器）

**使用专用配置：**

```bash
# 主数据库（MySQL，本地）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=prod123
DB_NAME=xhs_production
DB_DIALECT=mysql

# MongoDB（远程服务器，专用配置）
MONGODB_HOST=mongodb-prod.example.com
MONGODB_PORT=27017
MONGODB_USER=mongouser
MONGODB_PASSWORD=strong_password
MONGODB_DB_NAME=bettafish_prod
MONGODB_AUTH_SOURCE=admin
```

**切换到 MongoDB：**

```bash
# 1. 修改 DB_DIALECT
DB_DIALECT=mongodb

# 2. MongoDB 会自动使用 MONGODB_* 专用配置
python main.py --init_db mongodb
python main.py --platform xhs --type search --save_data_option mongodb
```

---

## 🔧 配置文件位置

所有配置逻辑在以下文件中实现：

### 1. **通用数据库配置** (`config/db_config.py`)

```python
# 读取 DB_DIALECT 决定数据库类型
DB_DIALECT = os.getenv("DB_DIALECT", "mysql")

# 读取通用配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "xhs")

# MySQL 配置（优先使用 MYSQL_* 专用配置，否则使用 DB_*）
MYSQL_DB_HOST = os.getenv("MYSQL_DB_HOST", DB_HOST)
MYSQL_DB_PORT = int(os.getenv("MYSQL_DB_PORT", str(DB_PORT) if DB_DIALECT == "mysql" else "3306"))

# PostgreSQL 配置（优先使用 POSTGRESQL_* 专用配置，否则使用 DB_*）
POSTGRESQL_DB_HOST = os.getenv("POSTGRESQL_DB_HOST", DB_HOST)
POSTGRESQL_DB_PORT = int(os.getenv("POSTGRESQL_DB_PORT", str(DB_PORT) if DB_DIALECT == "postgresql" else "5432"))
```

### 2. **MongoDB 配置** (`config/mongodb_config.py`)

```python
# 优先使用 MONGODB_* 专用配置，否则使用通用 DB_* 配置
MONGODB_HOST = os.getenv("MONGODB_HOST", os.getenv("DB_HOST", "localhost"))
MONGODB_PORT = int(os.getenv("MONGODB_PORT", os.getenv("DB_PORT", "27017")))
MONGODB_USER = os.getenv("MONGODB_USER", os.getenv("DB_USER", ""))
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", os.getenv("DB_PASSWORD", ""))
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", os.getenv("DB_NAME", "bettafish"))
```

### 3. **数据库初始化** (`database/db.py`)

```python
async def init_table_schema(db_type: str):
    """根据 db_type 初始化不同的数据库"""
    if db_type == "mongodb":
        # 测试连接
        if not await test_mongodb_connection():
            return False
        # 初始化索引
        if not await init_mongodb_indexes():
            return False
    else:
        # SQL 数据库初始化
        await create_tables(db_type)
```

---

## 📊 配置对照表

| 数据库 | DB_DIALECT | DB_PORT | 命令行参数 | 安装命令 |
|--------|-----------|---------|-----------|---------|
| MySQL | `mysql` | 3306 | `--save_data_option db` | 默认已安装 |
| PostgreSQL | `postgresql` | 5432 | `--save_data_option postgresql` | 默认已安装 |
| MongoDB | `mongodb` | 27017 | `--save_data_option mongodb` | `pip install motor` |

---

## ✅ 验证配置

### 测试 MongoDB 连接

```bash
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

## 🐞 常见问题

### Q1: 修改 DB_DIALECT 后需要重启程序吗？

**需要！** 配置在程序启动时加载，修改后需要重启爬虫程序。

### Q2: 可以同时使用多个数据库吗？

**可以！** 但需要使用专用配置：

```bash
# 方式1：环境变量
DB_DIALECT=mysql
MONGODB_HOST=mongodb-server.com

# 方式2：在代码中显式指定
python main.py --save_data_option mongodb
```

### Q3: 切换数据库后原有数据会丢失吗？

**不会！** 
- MySQL 数据保存在 MySQL 中
- MongoDB 数据保存在 MongoDB 中
- 两者相互独立

如果需要数据迁移，可以：
1. 导出为 CSV：`--save_data_option csv`
2. 写脚本导入新数据库

### Q4: MongoDB 必须安装 motor 包吗？

**是的！** MongoDB 异步操作需要 `motor`：

```bash
pip install motor==3.3.2
```

或使用专用依赖文件：

```bash
pip install -r requirements-mongodb.txt
```

### Q5: 端口号必须修改吗？

**建议修改，但不是必须：**

- 如果 MongoDB 运行在非标准端口（如 3306），可以不改
- 标准情况下：
  - MySQL: 3306
  - PostgreSQL: 5432
  - MongoDB: 27017

### Q6: 忘记修改端口会怎样？

**可能连接失败：**

```bash
# 错误示例：使用 MySQL 端口连接 MongoDB
DB_PORT=3306
DB_DIALECT=mongodb

# 错误：无法连接到 MongoDB（因为 MongoDB 实际运行在 27017）
```

**正确做法：**

```bash
DB_PORT=27017
DB_DIALECT=mongodb
```

---

## 🎉 总结

### 统一配置的优势

✅ **简单易用** - 只需修改 `DB_DIALECT` 参数  
✅ **向后兼容** - 支持专用 `MONGODB_*` 配置  
✅ **灵活切换** - MySQL、PostgreSQL、MongoDB 自由切换  
✅ **配置复用** - 一套配置参数适用所有数据库  

### 核心理念

> **"一个参数切换数据库"**  
> 不需要学习新的配置方式，不需要修改多个参数，只需改变 `DB_DIALECT` 的值。

---

## 📚 相关文档

- **快速切换指南**: `MongoDB快速切换指南.md`
- **详细使用指南**: `docs/MongoDB使用指南.md`
- **集成说明**: `MongoDB集成说明.md`
- **配置示例**: `config/env.mongodb.example`

---

## 💡 最佳实践

### 开发环境

```bash
# 使用 SQLite（无需安装数据库）
DB_DIALECT=sqlite

# 或使用 Docker 快速启动 MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:7.0
DB_DIALECT=mongodb
DB_PORT=27017
```

### 测试环境

```bash
# 使用 Docker Compose 统一管理
services:
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
  
  mongodb:
    image: mongo:7.0
    ports: ["27017:27017"]

# 根据测试需求切换
DB_DIALECT=mysql   # 测试 SQL 功能
DB_DIALECT=mongodb # 测试 NoSQL 功能
```

### 生产环境

```bash
# 使用云服务
DB_HOST=rds.cloud.com        # RDS MySQL
DB_DIALECT=mysql

# 或
DB_HOST=mongodb.cloud.com    # MongoDB Atlas
DB_DIALECT=mongodb
MONGODB_AUTH_SOURCE=admin
```

---

**祝你使用愉快！** 🎊

如有问题，请参考详细文档或提交 Issue。




