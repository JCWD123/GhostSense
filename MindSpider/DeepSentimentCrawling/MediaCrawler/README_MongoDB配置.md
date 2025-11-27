# MongoDB 配置快速参考

## 🎯 一句话总结

**只需修改 `.env` 中的 `DB_DIALECT=mongodb`，其他配置保持不变！**

---

## ⚡ 快速开始

### 1. 你的现有配置（`.env` 文件）

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_DIALECT=mysql          # 👈 当前使用 MySQL
```

### 2. 切换到 MongoDB

**只改两行：**

```bash
DB_HOST=localhost
DB_PORT=27017             # 👈 改为 MongoDB 端口
DB_USER=root
DB_PASSWORD=MyPassw0rd!
DB_NAME=xhs
DB_DIALECT=mongodb        # 👈 改为 mongodb
```

### 3. 运行

```bash
# 安装 MongoDB 依赖
pip install motor==3.3.2

# 初始化 MongoDB
python main.py --init_db mongodb

# 开始爬取
python main.py --platform xhs --type search --save_data_option mongodb
```

**完成！** ✅

---

## 🐳 Docker 快速启动 MongoDB

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=MyPassw0rd! \
  -e MONGO_INITDB_DATABASE=xhs \
  -v mongodb_data:/data/db \
  mongo:7.0
```

---

## 📊 配置对照

| 配置项 | MySQL | MongoDB |
|-------|-------|---------|
| DB_DIALECT | `mysql` | `mongodb` |
| DB_PORT | `3306` | `27017` |
| 其他配置 | 保持不变 | 保持不变 |

---

## 🔧 高级配置（可选）

如果需要 MongoDB 使用不同的配置，可以添加专用参数：

```bash
# 通用配置（MySQL 使用）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password1
DB_NAME=xhs

# MongoDB 专用配置（优先级更高）
MONGODB_HOST=mongodb-server.com
MONGODB_PORT=27017
MONGODB_USER=mongouser
MONGODB_PASSWORD=mongopass
MONGODB_DB_NAME=bettafish
```

**配置优先级：** `MONGODB_*` > `DB_*` > 默认值

---

## 📚 详细文档

- **统一配置说明**: `MongoDB统一配置说明.md`
- **快速切换指南**: `MongoDB快速切换指南.md`
- **详细使用指南**: `docs/MongoDB使用指南.md`

---

## ✅ 验证

```bash
python examples/test_mongodb.py
```

预期输出：
```
✅ MongoDB 连接成功！
✅ 索引创建成功！
✅ 数据存储测试成功！
🎉 所有测试通过！
```

---

## 🐞 常见问题

**Q: 必须安装 motor 吗？**  
A: 是的，MongoDB 需要：`pip install motor==3.3.2`

**Q: 切换数据库后原有数据会丢失吗？**  
A: 不会，MySQL 和 MongoDB 数据相互独立。

**Q: 可以同时使用多个数据库吗？**  
A: 可以，使用专用配置（`MONGODB_*`）即可。

---

**现在，你只需修改一个参数，就能切换数据库！** 🚀




