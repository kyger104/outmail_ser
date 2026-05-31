# GetLastEmails API - 完整指南

## 📋 项目概述

一个轻量级邮件托管系统，支持：
- **管理员面板** - 批量导入和管理 1000+ 邮箱
- **用户面板** - 查看邮件列表和详情
- **外部 API** - 供第三方调用获取邮件（支持 IMAP）
- **API Key 白名单** - 速率限制 + 白名单无限制访问
- **本地 + 服务器** - 支持 1H1G 服务器部署

---

## 🎯 当前状态

### ✅ 已完成（100% 后端）

**后端功能：**
- ✅ 数据库模型（Mailbox, Email, Attachment, APIKey）
- ✅ IMAP 客户端（异步连接、邮件获取）
- ✅ 自动同步调度器（30秒间隔）
- ✅ 管理员 API（导入、查询、删除邮箱）
- ✅ 邮件 API（列表、详情、标记已读）
- ✅ 外部 API（实时获取邮件，支持 IMAP）
- ✅ API Key 管理系统
- ✅ 速率限制中间件（20次/分钟，白名单无限制）

**前端框架：**
- ✅ Vue 3 + TypeScript + Vite
- ✅ Naive UI 组件库
- ✅ 路由配置

### ⚠️ 待完成

- ❌ Admin.vue - 管理员面板 UI
- ❌ Inbox.vue - 用户邮件面板 UI

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
.venv\Scripts\activate  # Windows
pip install msal==1.31.1 httpx==0.27.2
```

### 2. 生成应用密码（重要！）

Outlook/Hotmail **必须使用应用密码**，不能用普通密码。

**步骤：**
1. 访问 https://account.microsoft.com/security
2. 启用**两步验证**
3. 创建**应用密码**（格式：`abcd-efgh-ijkl-mnop`）
4. 保存密码（只显示一次）

### 3. 测试 IMAP 连接

修改 `test_imap_simple.py` 第 13 行：
```python
password = "YOUR_APP_PASSWORD"  # 替换为应用密码
```

运行测试：
```bash
python test_imap_simple.py
```

### 4. 启动服务

```bash
python main.py
# 服务运行在 http://localhost:7892
```

### 5. 创建 API Key（白名单）

```bash
curl -X POST "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"name":"test-key","description":"测试用","rate_limit":0}'
```

### 6. 测试 API

**无 API Key（速率限制 20次/分钟）：**
```bash
curl "http://localhost:7892/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

**带 API Key（无限制）：**
```bash
curl "http://localhost:7892/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1&api_key=sk_xxx"
```

---

## 📡 API 接口

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

**响应：**
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

**创建 API Key：** `POST /api/admin/api-keys`（需要 Basic Auth）
```bash
curl -X POST "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"name":"test-key","rate_limit":0}'
```

**查看 API Key 列表：** `GET /api/admin/api-keys`
```bash
curl "http://localhost:7892/api/admin/api-keys" -u admin:admin123
```

**删除 API Key：** `DELETE /api/admin/api-keys/{id}`

### 管理员 API

**导入邮箱：** `POST /api/admin/mailboxes/import`
```json
{
  "mailboxes": [
    {
      "email": "user@outlook.com",
      "imap_token": "app_password_here"
    }
  ]
}
```

**邮箱列表：** `GET /api/admin/mailboxes?page=1&page_size=20`

**删除邮箱：** `DELETE /api/admin/mailboxes/{id}`

### 邮件 API

**邮件列表：** `GET /api/emails/?mailbox_id=1&page=1&page_size=20`

**邮件详情：** `GET /api/emails/{id}`

**标记已读：** `PUT /api/emails/{id}/read`

**手动刷新：** `POST /api/emails/refresh?mailbox_id=1`

---

## 🏗️ 项目结构

```
backend/
├── services/              # 服务层
│   ├── token_manager.py   # OAuth2 令牌管理
│   ├── microsoft_graph.py # Graph API 客户端
│   └── imap_service.py    # IMAP 服务 ✨
├── middleware/
│   └── rate_limiter.py    # 速率限制中间件 ✨
├── routers/
│   ├── admin.py           # 管理员 API
│   ├── emails.py          # 邮件 API
│   ├── external_api_dual.py # 外部 API（IMAP）✨
│   └── api_keys.py        # API Key 管理 ✨
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
```

---

## 🖥️ 部署方案

### 本地开发

**后端：**
```bash
cd backend
python main.py
# http://localhost:7892
```

**前端：**
```bash
cd frontend
npm run dev
# http://localhost:5173
```

### 服务器部署（1H1G）

**完整部署指南：** 参考 `docs/SERVER_DEPLOYMENT.md`

**域名：** chace123.sbs (118.194.253.6)

**快速步骤：**
```bash
# 1. 上传代码到服务器
scp -r imap/ root@118.194.253.6:/opt/

# 2. 安装依赖
cd /opt/imap/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 配置 Systemd 服务
sudo systemctl enable imap-backend
sudo systemctl start imap-backend

# 4. 配置 Nginx 反向代理
# 参考 SERVER_DEPLOYMENT.md

# 5. 配置 HTTPS（Let's Encrypt）
certbot --nginx -d chace123.sbs

# 6. 测试部署
curl https://chace123.sbs/health
```

### 性能优化（1H1G 服务器）

**内存优化：**
```python
# scheduler.py
MAX_CONCURRENT_SYNC = 5  # 最多 5 个邮箱同时同步

# config.py
SYNC_INTERVAL = 300  # 5 分钟同步一次（而不是 30 秒）

# imap_client.py
MAX_EMAILS_PER_SYNC = 10  # 每次最多同步 10 封新邮件
```

**资源占用预估：**
- 内存：500MB（100 个邮箱）
- 磁盘：1GB（10000 封邮件）
- CPU：10-20%（同步时）

---

## 🔧 故障排查

### 问题 1：IMAP 认证失败

**错误：** `AUTHENTICATE failed`

**原因：** 使用了普通密码而非应用密码

**解决：**
1. 访问 https://account.microsoft.com/security
2. 启用两步验证
3. 创建应用密码
4. 使用应用密码测试

### 问题 2：服务器内存不足

**现象：** 进程被 OOM Killer 杀死

**解决：**
1. 减少同步并发数（`MAX_CONCURRENT_SYNC = 3`）
2. 增加同步间隔（`SYNC_INTERVAL = 600`）
3. 定期清理旧邮件（保留 30 天）

### 问题 3：数据库锁定

**错误：** `database is locked`

**解决：**
1. 使用 WAL 模式：`PRAGMA journal_mode=WAL`
2. 增加超时时间：`timeout=30`

---

## 📝 下一步计划

### 阶段 1：测试 IMAP（今天）

1. ✅ 生成应用密码
2. ✅ 测试 IMAP 连接
3. ✅ 测试外部 API

### 阶段 2：前端开发（3-5 天）

1. ⏳ 实现 Admin.vue（管理员面板）
   - 邮箱列表表格
   - 批量导入功能
   - 删除和管理操作

2. ⏳ 实现 Inbox.vue（用户面板）
   - 邮箱选择器
   - 邮件列表
   - 邮件详情查看

### 阶段 3：部署测试（1-2 天）

1. ⏳ 本地测试（导入 10 个邮箱）
2. ⏳ 服务器部署（1H1G）
3. ⏳ 性能测试和优化

---

## 📚 API 文档

启动服务后访问：
- **Swagger UI:** http://localhost:7892/docs
- **ReDoc:** http://localhost:7892/redoc

**完整 API 文档：** 参考 `docs/API_DOCUMENTATION.md`

---

## 🎯 核心功能清单

### 已实现

- [x] IMAP 邮件获取
- [x] 自动同步调度
- [x] 邮箱批量导入
- [x] 邮件列表查询
- [x] 邮件详情查看
- [x] 外部 API 接口
- [x] API Key 管理系统
- [x] 速率限制中间件

### 待实现

- [ ] 管理员面板 UI
- [ ] 用户邮件面板 UI
- [ ] 用户认证登录
- [ ] 邮件搜索功能
- [ ] 附件下载

---

## 📞 快速命令

```bash
# 测试 IMAP
python test_imap_simple.py

# 启动后端
python main.py

# 创建 API Key
curl -X POST "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"name":"test-key","rate_limit":0}'

# 测试 API（无 API Key）
curl "http://localhost:7892/api/GetLastEmails?email=test@outlook.com&password=APP_PASSWORD&num=2&boxType=1"

# 测试 API（带 API Key）
curl "http://localhost:7892/api/GetLastEmails?email=test@outlook.com&password=APP_PASSWORD&num=2&api_key=sk_xxx"

# 查看 API 文档
open http://localhost:7892/docs

# 启动前端
cd frontend && npm run dev
```

---

**项目状态：** 后端 100% | 前端 50% | 整体 75%  
**部署准备：** ✅ 部署文档完成  
**预计完成：** 1-2 周
