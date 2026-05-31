# GetLastEmails API - 轻量级邮件托管系统

一个轻量级的 Hotmail/Outlook 邮件托管系统，支持：
- **管理员面板** - 批量导入和管理 1000+ 邮箱
- **用户面板** - 查看邮件列表和详情
- **外部 API** - 供第三方调用获取邮件（支持 IMAP）
- **API Key 白名单** - 速率限制 + 白名单无限制访问
- **本地 + 服务器** - 支持 1H1G 服务器部署

## 项目状态

✅ **后端完成 100%** - IMAP 服务、API 接口、API Key 管理、速率限制  
✅ **外部 API** - 实时获取邮件接口（IMAP 方式）  
✅ **速率限制** - 普通用户 20次/分钟，白名单无限制  
✅ **本地测试** - 所有功能测试通过  
⚠️ **前端待完成** - Admin.vue 和 Inbox.vue UI 组件  
⚠️ **生产部署** - 需要部署到服务器

## 技术栈

**后端:**
- FastAPI + aioimaplib（IMAP 客户端）
- SQLite + SQLAlchemy
- API Key 管理 + 速率限制中间件
- 自动同步调度器（30秒间隔）

**前端:**
- Vue 3 + TypeScript + Naive UI

**部署:**
- 端口：7892（不常见端口，避免冲突）
- 支持 Nginx 反向代理 + HTTPS
- 1H1G 服务器 + swap  

## 快速开始

### 1. 生成应用密码（重要！）

Outlook/Hotmail **必须使用应用密码**，不能用普通密码。

**步骤：**
1. 访问 https://account.microsoft.com/security
2. 启用**两步验证**
3. 创建**应用密码**（格式：`abcd-efgh-ijkl-mnop`）
4. 保存密码（只显示一次）

详细说明：[HOW_TO_GET_APP_PASSWORD.md](HOW_TO_GET_APP_PASSWORD.md)

### 2. 测试 IMAP 连接

修改 `backend/test_imap_simple.py` 第 20 行：
```python
password = "YOUR_APP_PASSWORD"  # 替换为应用密码
```

运行测试：
```bash
cd backend
python test_imap_simple.py
```

### 3. 启动服务

```bash
cd backend
python main.py
# 服务运行在 http://localhost:7892
```

### 4. 创建 API Key（白名单）

```bash
curl -X POST "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"name":"test-key","description":"测试用","rate_limit":0}'
```

**响应示例：**
```json
{
  "id": 1,
  "api_key": "sk_xxxxxxxxxxxxxxxxx",
  "name": "test-key",
  "rate_limit": 0,
  "is_active": true
}
```

### 5. 测试外部 API

**无 API Key（速率限制 20次/分钟）：**
```bash
curl "http://localhost:7892/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

**带 API Key（无限制）：**
```bash
curl "http://localhost:7892/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1&api_key=sk_xxx"
```

## API 接口

### 外部 API（实时获取邮件）

**接口：** `GET /api/GetLastEmails`

**参数：**
- `email` (必填) - 邮箱地址
- `password` (必填) - 应用密码
- `num` (可选, 1-5, 默认1) - 获取数量
- `boxType` (可选, 1或2, 默认1) - 1=收件箱, 2=垃圾箱
- `api_key` (可选) - API Key（白名单用户无速率限制）

**速率限制：**
- 普通用户：20次/分钟（基于 IP）
- 白名单用户：无限制（需要 API Key）

**响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "Date": "2026-05-31 10:30:00",
      "From": "Sender <sender@example.com>",
      "To": "Recipient <recipient@example.com>",
      "Subject": "Email subject",
      "Body": "<html>...</html>",
      "BodyPreview": "Email preview...",
      "HasAttachments": false,
      "IsRead": false
    }
  ]
}
```

### API Key 管理

- `POST /api/admin/api-keys` - 创建 API Key（需要 Basic Auth）
- `GET /api/admin/api-keys` - 查看 API Key 列表
- `DELETE /api/admin/api-keys/{id}` - 删除 API Key

### 管理员 API

- `POST /api/admin/mailboxes/import` - 批量导入邮箱
- `GET /api/admin/mailboxes` - 邮箱列表
- `DELETE /api/admin/mailboxes/{id}` - 删除邮箱

### 邮件 API

- `GET /api/emails/` - 邮件列表
- `GET /api/emails/{id}` - 邮件详情
- `PUT /api/emails/{id}/read` - 标记已读
- `POST /api/emails/refresh` - 手动刷新

完整文档：http://localhost:7892/docs

## 项目结构

```
backend/
├── services/              # 服务层
│   ├── imap_service.py    # IMAP 服务
│   ├── token_manager.py   # OAuth2 令牌管理
│   └── microsoft_graph.py # Graph API 客户端
├── middleware/
│   └── rate_limiter.py    # 速率限制中间件
├── routers/
│   ├── admin.py           # 管理员 API
│   ├── emails.py          # 邮件 API
│   ├── external_api_dual.py # 外部 API（IMAP）
│   └── api_keys.py        # API Key 管理
├── models.py              # 数据模型（含 APIKey）
├── database.py            # 数据库连接
├── scheduler.py           # 同步调度器
├── config.py              # 配置（端口 7892）
└── main.py                # FastAPI 主应用

frontend/
├── src/
│   ├── views/
│   │   ├── Admin.vue      # 管理员面板（待实现）
│   │   └── Inbox.vue      # 用户面板（待实现）
│   └── utils/api.ts       # API 客户端
└── package.json

data/
├── emails.db              # SQLite 数据库
└── attachments/           # 附件存储

docs/
├── API_DOCUMENTATION.md   # API 详细文档
├── FRONTEND_DEV_TASK.md   # 前端开发任务
├── GUIDE.md               # 完整使用指南
├── HOW_TO_GET_APP_PASSWORD.md # 应用密码指南
├── LOCAL_TEST_GUIDE.md    # 本地测试指南
├── PROJECT_SUMMARY.md     # 项目总结
├── SERVER_DEPLOYMENT.md   # 服务器部署指南
└── TEST_REPORT.md         # 测试报告
```

## 文档

- **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - API 详细文档
- **[docs/LOCAL_TEST_GUIDE.md](docs/LOCAL_TEST_GUIDE.md)** - 本地测试指南
- **[docs/SERVER_DEPLOYMENT.md](docs/SERVER_DEPLOYMENT.md)** - 服务器部署指南
- **[docs/FRONTEND_DEV_TASK.md](docs/FRONTEND_DEV_TASK.md)** - 前端开发任务
- **[docs/HOW_TO_GET_APP_PASSWORD.md](docs/HOW_TO_GET_APP_PASSWORD.md)** - 应用密码生成指南
- **[docs/GUIDE.md](docs/GUIDE.md)** - 完整使用指南
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - 项目总结
- **[docs/TEST_REPORT.md](docs/TEST_REPORT.md)** - 测试报告

## 下一步

1. ✅ 生成应用密码
2. ✅ 测试 IMAP 连接
3. ✅ 创建 API Key 管理
4. ✅ 实现速率限制
5. ⏳ 实现前端 UI（Admin.vue, Inbox.vue）
6. ⏳ 服务器部署（参考 docs/SERVER_DEPLOYMENT.md）

---

**当前状态：** 后端完成，前端待开发  
**部署准备：** 已完成（参考 SERVER_DEPLOYMENT.md）  
**测试状态：** 本地测试通过
