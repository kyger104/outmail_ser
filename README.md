# GetLastEmails API - 轻量级邮件托管系统

一个轻量级的 Hotmail/Outlook 邮件托管系统，支持：
- **管理员面板** - 批量导入和管理 1000+ 邮箱
- **用户面板** - 查看邮件列表和详情
- **外部 API** - 供第三方调用获取邮件（支持 IMAP）
- **本地 + 服务器** - 支持 1H1G 服务器部署

## 项目状态

✅ **后端完成 90%** - IMAP 服务、API 接口、自动同步调度器  
✅ **外部 API** - 实时获取邮件接口（IMAP 方式）  
⚠️ **前端待完成** - Admin.vue 和 Inbox.vue UI 组件  
⚠️ **IMAP 测试** - 需要应用密码验证连接

## 技术栈

**后端:**
- FastAPI + aioimaplib（IMAP 客户端）
- SQLite + SQLAlchemy
- 自动同步调度器（30秒间隔）

**前端:**
- Vue 3 + TypeScript + Naive UI  

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
# 服务运行在 http://localhost:8000
```

### 4. 测试外部 API

```bash
curl "http://localhost:8000/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

## API 接口

### 外部 API（实时获取邮件）

**接口：** `GET /api/GetLastEmails`

**参数：**
- `email` (必填) - 邮箱地址
- `password` (必填) - 应用密码
- `num` (可选, 1-5, 默认1) - 获取数量
- `boxType` (可选, 1或2, 默认1) - 1=收件箱, 2=垃圾箱

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

### 管理员 API

- `POST /api/admin/mailboxes/import` - 批量导入邮箱
- `GET /api/admin/mailboxes` - 邮箱列表
- `DELETE /api/admin/mailboxes/{id}` - 删除邮箱

### 邮件 API

- `GET /api/emails/` - 邮件列表
- `GET /api/emails/{id}` - 邮件详情
- `PUT /api/emails/{id}/read` - 标记已读
- `POST /api/emails/refresh` - 手动刷新

完整文档：http://localhost:8000/docs

## 项目结构

```
backend/
├── services/              # 服务层
│   ├── imap_service.py    # IMAP 服务
│   ├── token_manager.py   # OAuth2 令牌管理
│   └── microsoft_graph.py # Graph API 客户端
├── routers/
│   ├── admin.py           # 管理员 API
│   ├── emails.py          # 邮件 API
│   └── external_api_dual.py # 外部 API（IMAP）
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

## 文档

- **[GUIDE.md](GUIDE.md)** - 完整使用指南（API、部署、故障排查）
- **[HOW_TO_GET_APP_PASSWORD.md](HOW_TO_GET_APP_PASSWORD.md)** - 应用密码生成指南

## 下一步

1. ✅ 生成应用密码
2. ✅ 测试 IMAP 连接
3. ⏳ 实现前端 UI（Admin.vue, Inbox.vue）
4. ⏳ 服务器部署（1H1G）

---

**当前阻塞：** 需要应用密码测试 IMAP  
**预计完成：** 1-2 周
