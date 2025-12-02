# MediaCrawer Pro API 文档

## 基础信息

- **Base URL**: `http://localhost:8888`
- **响应格式**: JSON
- **字符编码**: UTF-8

## 响应格式

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 错误响应

```json
{
  "code": 1,
  "message": "错误信息",
  "data": null
}
```

## API 接口

### 1. 健康检查

**GET** `/health`

检查服务是否正常运行。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "app_name": "MediaCrawer Pro"
  }
}
```

---

### 2. 任务管理

#### 2.1 创建任务

**POST** `/api/v1/tasks`

创建一个新的爬取任务。

**请求参数：**

```json
{
  "platform": "xhs",              // 平台：xhs, douyin, kuaishou, bilibili
  "type": "search",               // 类型：search, homefeed, note
  "keywords": ["Python", "编程"],  // 关键词列表（type=search 时必填）
  "max_count": 100,               // 最大爬取数量
  "enable_comment": true,         // 是否爬取评论
  "enable_download": false        // 是否下载视频
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "任务创建成功",
  "data": {
    "task_id": "uuid-xxxx-xxxx",
    "platform": "xhs",
    "type": "search",
    "status": "pending",
    "created_at": "2024-01-01 12:00:00"
  }
}
```

#### 2.2 获取任务列表

**GET** `/api/v1/tasks`

获取任务列表，支持分页和筛选。

**查询参数：**

- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20
- `status`: 状态筛选（pending, running, completed, failed）
- `platform`: 平台筛选（xhs, douyin, kuaishou, bilibili）

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "task_id": "uuid-xxxx-xxxx",
        "platform": "xhs",
        "type": "search",
        "keywords": ["Python"],
        "status": "running",
        "progress": {
          "total": 100,
          "crawled": 45,
          "success": 43,
          "failed": 2
        },
        "created_at": "2024-01-01 12:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

#### 2.3 获取任务详情

**GET** `/api/v1/tasks/{task_id}`

获取指定任务的详细信息。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "uuid-xxxx-xxxx",
    "platform": "xhs",
    "type": "search",
    "keywords": ["Python"],
    "status": "completed",
    "progress": {
      "total": 100,
      "crawled": 100,
      "success": 98,
      "failed": 2
    },
    "created_at": "2024-01-01 12:00:00",
    "started_at": "2024-01-01 12:00:05",
    "completed_at": "2024-01-01 12:15:30"
  }
}
```

#### 2.4 删除任务

**DELETE** `/api/v1/tasks/{task_id}`

删除指定任务及其断点数据。

**响应示例：**

```json
{
  "code": 0,
  "message": "任务删除成功",
  "data": null
}
```

---

### 3. 视频下载

#### 3.1 下载视频/图片

**POST** `/api/v1/download`

下载指定 URL 的视频或图片。

**请求参数：**

```json
{
  "url": "https://example.com/video.mp4",  // 下载链接
  "save_path": "/path/to/save",            // 保存路径（可选）
  "filename": "my_video.mp4"               // 文件名（可选）
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "下载成功",
  "data": {
    "success": true,
    "file_path": "/downloads/my_video.mp4",
    "file_size": 25600000
  }
}
```

---

### 4. 账号管理

#### 4.1 获取账号列表

**GET** `/api/v1/accounts`

获取账号池中的所有账号。

**查询参数：**

- `platform`: 平台筛选
- `status`: 状态筛选（active, inactive, banned）

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "_id": "account-id-1",
      "platform": "xhs",
      "cookie": "xxx...xxx",  // 脱敏显示
      "status": "active",
      "weight": 1,
      "use_count": 50,
      "success_count": 48,
      "fail_count": 2,
      "success_rate": 96.0,
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

#### 4.2 添加账号

**POST** `/api/v1/accounts`

添加新账号到账号池。

**请求参数：**

```json
{
  "platform": "xhs",       // 平台
  "cookie": "xxx...",      // 完整的 Cookie
  "weight": 1,             // 权重（1-10）
  "status": "active",      // 状态
  "note": "备注信息"       // 备注（可选）
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "账号添加成功",
  "data": {
    "_id": "account-id-1",
    "platform": "xhs",
    "status": "active",
    "created_at": "2024-01-01 12:00:00"
  }
}
```

#### 4.3 删除账号

**DELETE** `/api/v1/accounts/{account_id}`

从账号池中删除指定账号。

**响应示例：**

```json
{
  "code": 0,
  "message": "账号删除成功",
  "data": null
}
```

---

### 5. 代理管理

#### 5.1 获取代理列表

**GET** `/api/v1/proxies`

获取代理池中的所有代理。

**查询参数：**

- `status`: 状态筛选（active, inactive, banned）

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "_id": "proxy-id-1",
      "proxy_url": "http://127.0.0.1:7890",
      "provider": "custom",
      "status": "active",
      "use_count": 100,
      "success_count": 98,
      "fail_count": 2,
      "success_rate": 98.0,
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

#### 5.2 添加代理

**POST** `/api/v1/proxies`

添加新代理到代理池。

**请求参数：**

```json
{
  "protocol": "http",      // 协议：http, https, socks5
  "host": "127.0.0.1",     // 主机地址
  "port": 7890,            // 端口
  "username": "",          // 用户名（可选）
  "password": "",          // 密码（可选）
  "provider": "custom"     // 提供商
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "代理添加成功",
  "data": {
    "_id": "proxy-id-1",
    "proxy_url": "http://127.0.0.1:7890",
    "status": "active",
    "created_at": "2024-01-01 12:00:00"
  }
}
```

---

### 6. 断点续爬

#### 6.1 获取断点列表

**GET** `/api/v1/checkpoints`

获取所有断点信息。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "task_id": "uuid-xxxx-xxxx",
      "checkpoint_data": {
        "current_page": 5,
        "current_keyword": "Python",
        "crawled_count": 50
      },
      "checkpoint_time": "2024-01-01 12:10:00",
      "status": "active"
    }
  ]
}
```

#### 6.2 获取指定任务的断点

**GET** `/api/v1/checkpoints/{task_id}`

获取指定任务的断点信息，用于恢复爬取。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "uuid-xxxx-xxxx",
    "checkpoint_data": {
      "current_page": 5,
      "current_keyword": "Python",
      "crawled_count": 50
    },
    "checkpoint_time": "2024-01-01 12:10:00"
  }
}
```

---

### 7. 首页推荐流

#### 7.1 获取平台推荐流

**GET** `/api/v1/homefeed`

获取指定平台的首页推荐内容。

**查询参数：**

- `platform`: 平台（xhs, douyin, kuaishou, bilibili）
- `page`: 页码

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "platform": "xhs",
    "items": [
      {
        "note_id": "xxx",
        "title": "标题",
        "desc": "描述",
        "type": "video",
        "user_id": "xxx",
        "nickname": "用户昵称",
        "liked_count": "1000",
        "image_list": ["url1", "url2"],
        "video_url": "video_url"
      }
    ],
    "cursor": "next_cursor",
    "has_more": true
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

# 创建任务
response = requests.post('http://localhost:8888/api/v1/tasks', json={
    "platform": "xhs",
    "type": "search",
    "keywords": ["Python", "编程"],
    "max_count": 100,
    "enable_comment": True
})

result = response.json()
task_id = result['data']['task_id']

print(f"任务创建成功，ID: {task_id}")

# 查询任务状态
response = requests.get(f'http://localhost:8888/api/v1/tasks/{task_id}')
task_info = response.json()

print(f"任务状态: {task_info['data']['status']}")
print(f"爬取进度: {task_info['data']['progress']}")
```

### JavaScript 示例

```javascript
// 创建任务
const response = await fetch('http://localhost:8888/api/v1/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    platform: 'xhs',
    type: 'search',
    keywords: ['Python', '编程'],
    max_count: 100,
    enable_comment: true
  })
});

const result = await response.json();
const taskId = result.data.task_id;

console.log(`任务创建成功，ID: ${taskId}`);

// 查询任务状态
const taskResponse = await fetch(`http://localhost:8888/api/v1/tasks/${taskId}`);
const taskInfo = await taskResponse.json();

console.log(`任务状态: ${taskInfo.data.status}`);
console.log(`爬取进度:`, taskInfo.data.progress);
```




