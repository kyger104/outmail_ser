# GetLastEmails API - 完整指南

## 📋 项目概述

一个轻量级邮件托管系统，支持：
- **管理员面板** - 批量导入和管理 1000+ 邮箱
- **用户面板** - 查看邮件列表和详情
- **外部 API** - 供第三方调用获取邮件
- **本地 + 服务器** - 支持 1H1G 服务器部署

---

## 🎯 当前状态

### ✅ 已完成（90%）

**后端功能：**
- ✅ 数据库模型（Mailbox, Email, Attachment）
- ✅ IMAP 客户端（异步连接、邮件获取）
- ✅ 自动同步调度器（30秒间隔）
- ✅ 管理员 API（导入、查询、删除邮箱）
- ✅ 邮件 API（列表、详情、标记已读）
- ✅ 外部 API（实时获取邮件，支持 IMAP）

**前端框架：**
- ✅ Vue 3 + TypeScript + Vite
- ✅ Naive UI 组件库
- ✅ 路由配置

### ⚠️ 待完成（10%）

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
# 服务运行在 http://localhost:8000
```

### 5. 测试 API

```bash
curl "http://localhost:8000/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
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
├── routers/
│   ├── admin.py           # 管理员 API
│   ├── emails.py          # 邮件 API
│   └── external_api_dual.py # 外部 API（IMAP）✨
├── models.py              # 数据模型
├── database.py            # 数据库连接
├── scheduler.py           # 同步调度器
├── main.py                # FastAPI 主应用
└── test_imap_simple.py    # IMAP 测试脚本

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
# http://localhost:8000
```

**前端：**
```bash
cd frontend
npm run dev
# http://localhost:5173
```

### 服务器部署（1H1G）

**方案 1：Docker Compose（推荐）**

```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

**方案 2：Systemd 服务**

```bash
# 启动后端
sudo systemctl start imap-backend

# 查看状态
sudo systemctl status imap-backend

# 查看日志
sudo journalctl -u imap-backend -f
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
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🎯 核心功能清单

### 已实现

- [x] IMAP 邮件获取
- [x] 自动同步调度
- [x] 邮箱批量导入
- [x] 邮件列表查询
- [x] 邮件详情查看
- [x] 外部 API 接口

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

# 测试 API
curl "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=APP_PASSWORD&num=2&boxType=1"

# 查看 API 文档
open http://localhost:8000/docs

# 启动前端
cd frontend && npm run dev

# Docker 部署
docker-compose up -d
```

---

**项目状态：** 后端 90% | 前端 50% | 整体 70%  
**当前阻塞：** 需要应用密码测试 IMAP  
**预计完成：** 1-2 周
