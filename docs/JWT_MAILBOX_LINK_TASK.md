# 邮箱管理系统 - 前后端开发任务

## 项目背景

这是一个 Hotmail/Outlook 邮箱托管系统，已完成后端 API 和基础架构。现在需要实现：
1. **JWT 邮箱链接功能** - 为每个邮箱生成专属访问链接
2. **管理后台** - 管理邮箱、查看链接、管理 API Key
3. **邮箱查看页** - 用户通过 JWT 链接查看自己的邮件

## 技术栈

**后端：**
- FastAPI + Python 3.12
- SQLite + SQLAlchemy
- JWT 认证（PyJWT）
- IMAP 邮件获取

**前端：**
- Vue 3 + TypeScript
- Naive UI 组件库
- Vite 构建工具

**已完成：**
- ✅ 数据库模型（Mailbox 已添加 jwt_token 字段）
- ✅ IMAP 邮件获取服务
- ✅ API Key 管理和速率限制
- ✅ JWT 工具类（backend/utils/jwt_helper.py）

---

## 任务 1：后端 JWT 功能实现

### 1.1 修改管理员 API（backend/routers/admin.py）

**需要添加的功能：**

#### A. 导入邮箱时自动生成 JWT token

修改 `POST /api/admin/mailboxes/import` 接口：

```python
from utils.jwt_helper import JWTHelper

# 在创建邮箱后，生成 JWT token
for mailbox_data in request.mailboxes:
    # 创建邮箱
    db_mailbox = Mailbox(
        email=mailbox_data.email,
        imap_token=encrypted_token,
        # ... 其他字段
    )
    db.add(db_mailbox)
    db.flush()  # 获取 ID
    
    # 生成 JWT token
    jwt_token = JWTHelper.generate_mailbox_token(
        mailbox_id=db_mailbox.id,
        email=db_mailbox.email
    )
    db_mailbox.jwt_token = jwt_token
    
db.commit()
```

#### B. 添加获取邮箱链接的接口

新增接口：`GET /api/admin/mailboxes/{id}/link`

```python
@router.get("/mailboxes/{id}/link")
def get_mailbox_link(
    id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """获取邮箱的访问链接"""
    mailbox = db.query(Mailbox).filter(Mailbox.id == id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")
    
    # 如果没有 JWT token，生成一个
    if not mailbox.jwt_token:
        jwt_token = JWTHelper.generate_mailbox_token(
            mailbox_id=mailbox.id,
            email=mailbox.email
        )
        mailbox.jwt_token = jwt_token
        db.commit()
    
    link = JWTHelper.generate_mailbox_url(mailbox.jwt_token)
    
    return {
        "mailbox_id": mailbox.id,
        "email": mailbox.email,
        "jwt_token": mailbox.jwt_token,
        "link": link
    }
```

#### C. 批量获取所有邮箱链接

新增接口：`GET /api/admin/mailboxes/links`

```python
@router.get("/mailboxes/links")
def get_all_mailbox_links(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """批量获取所有邮箱的访问链接"""
    mailboxes = db.query(Mailbox).all()
    
    results = []
    for mailbox in mailboxes:
        # 如果没有 JWT token，生成一个
        if not mailbox.jwt_token:
            jwt_token = JWTHelper.generate_mailbox_token(
                mailbox_id=mailbox.id,
                email=mailbox.email
            )
            mailbox.jwt_token = jwt_token
        
        link = JWTHelper.generate_mailbox_url(mailbox.jwt_token)
        results.append({
            "id": mailbox.id,
            "email": mailbox.email,
            "link": link,
            "status": mailbox.status
        })
    
    db.commit()
    return {"items": results, "total": len(results)}
```

### 1.2 创建邮件查看 API（backend/routers/inbox.py）

**新建文件：** `backend/routers/inbox.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Mailbox, Email
from utils.jwt_helper import JWTHelper
from typing import Optional

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("/verify")
def verify_jwt(jwt: str, db: Session = Depends(get_db)):
    """验证 JWT token 并返回邮箱信息"""
    payload = JWTHelper.verify_mailbox_token(jwt)
    
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    
    mailbox_id = payload.get("mailbox_id")
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")
    
    return {
        "mailbox_id": mailbox.id,
        "email": mailbox.email,
        "status": mailbox.status
    }


@router.get("/emails")
def get_emails(
    jwt: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取邮箱的邮件列表（需要 JWT 验证）"""
    payload = JWTHelper.verify_mailbox_token(jwt)
    
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    
    mailbox_id = payload.get("mailbox_id")
    
    # 查询邮件
    query = db.query(Email).filter(Email.mailbox_id == mailbox_id)
    total = query.count()
    
    emails = query.order_by(Email.date.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return {
        "items": [
            {
                "id": email.id,
                "subject": email.subject,
                "sender": email.sender,
                "date": email.date.isoformat() if email.date else None,
                "is_read": email.is_read,
                "has_attachments": email.has_attachments,
                "body_preview": email.body_text[:200] if email.body_text else ""
            }
            for email in emails
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/emails/{email_id}")
def get_email_detail(
    email_id: int,
    jwt: str,
    db: Session = Depends(get_db)
):
    """获取邮件详情（需要 JWT 验证）"""
    payload = JWTHelper.verify_mailbox_token(jwt)
    
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    
    mailbox_id = payload.get("mailbox_id")
    
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.mailbox_id == mailbox_id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    
    # 标记为已读
    if not email.is_read:
        email.is_read = True
        db.commit()
    
    return {
        "id": email.id,
        "subject": email.subject,
        "sender": email.sender,
        "recipient": email.recipient,
        "date": email.date.isoformat() if email.date else None,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "has_attachments": email.has_attachments
    }
```

### 1.3 注册新路由（backend/main.py）

在 `main.py` 中添加：

```python
from routers import admin, emails, external_api_dual, api_keys, inbox

app.include_router(inbox.router)  # 新增
```

---

## 任务 2：前端管理后台开发（Admin.vue）

**文件位置：** `frontend/src/views/Admin.vue`

### 功能需求

1. **邮箱管理**
   - 显示邮箱列表（表格）
   - 批量导入邮箱（文本框输入，格式：email:password）
   - 删除邮箱
   - 显示邮箱状态

2. **链接管理**
   - 每个邮箱显示专属链接
   - 一键复制链接按钮
   - 批量导出所有链接（CSV 或 JSON）

3. **API Key 管理**
   - 创建 API Key
   - 查看 API Key 列表
   - 删除 API Key

### UI 设计参考

```
┌─────────────────────────────────────────────────────────┐
│  邮箱管理系统 - 管理后台                                  │
├─────────────────────────────────────────────────────────┤
│  [邮箱管理] [API Key 管理]                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  批量导入邮箱：                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ email1@outlook.com:password1                   │    │
│  │ email2@outlook.com:password2                   │    │
│  └────────────────────────────────────────────────┘    │
│  [导入邮箱] [导出所有链接]                               │
│                                                          │
│  邮箱列表：                                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ ID │ 邮箱地址          │ 状态  │ 访问链接 │ 操作 │    │
│  ├────┼──────────────────┼──────┼─────────┼─────┤    │
│  │ 1  │ test@outlook.com │ 正常 │ [复制]   │ 删除 │    │
│  │ 2  │ user@hotmail.com │ 正常 │ [复制]   │ 删除 │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 核心代码结构

```vue
<template>
  <n-space vertical>
    <n-card title="邮箱管理系统 - 管理后台">
      <n-tabs type="line">
        <!-- Tab 1: 邮箱管理 -->
        <n-tab-pane name="mailboxes" tab="邮箱管理">
          <!-- 批量导入 -->
          <n-space vertical>
            <n-input
              v-model:value="importText"
              type="textarea"
              placeholder="格式：email:password（每行一个）"
              :rows="5"
            />
            <n-button type="primary" @click="importMailboxes">
              导入邮箱
            </n-button>
            <n-button @click="exportLinks">
              导出所有链接
            </n-button>
          </n-space>

          <!-- 邮箱列表 -->
          <n-data-table
            :columns="mailboxColumns"
            :data="mailboxes"
            :loading="loading"
          />
        </n-tab-pane>

        <!-- Tab 2: API Key 管理 -->
        <n-tab-pane name="apikeys" tab="API Key 管理">
          <!-- API Key 创建和列表 -->
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpace, NCard, NTabs, NTabPane, NInput, NButton, NDataTable, useMessage } from 'naive-ui'
import axios from 'axios'

const message = useMessage()
const loading = ref(false)
const importText = ref('')
const mailboxes = ref([])

// 表格列定义
const mailboxColumns = [
  { title: 'ID', key: 'id' },
  { title: '邮箱地址', key: 'email' },
  { title: '状态', key: 'status' },
  {
    title: '访问链接',
    key: 'link',
    render: (row) => {
      return h(NButton, {
        size: 'small',
        onClick: () => copyLink(row.link)
      }, { default: () => '复制链接' })
    }
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => deleteMailbox(row.id)
      }, { default: () => '删除' })
    }
  }
]

// 加载邮箱列表
async function loadMailboxes() {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/mailboxes/links', {
      auth: {
        username: 'admin',
        password: 'admin123'
      }
    })
    mailboxes.value = response.data.items
  } catch (error) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 导入邮箱
async function importMailboxes() {
  const lines = importText.value.split('\n').filter(line => line.trim())
  const mailboxData = lines.map(line => {
    const [email, password] = line.split(':')
    return { email: email.trim(), imap_token: password.trim() }
  })

  try {
    await axios.post('/api/admin/mailboxes/import', {
      mailboxes: mailboxData
    }, {
      auth: {
        username: 'admin',
        password: 'admin123'
      }
    })
    message.success('导入成功')
    importText.value = ''
    loadMailboxes()
  } catch (error) {
    message.error('导入失败')
  }
}

// 复制链接
function copyLink(link: string) {
  navigator.clipboard.writeText(link)
  message.success('链接已复制')
}

// 导出链接
function exportLinks() {
  const data = mailboxes.value.map(m => `${m.email},${m.link}`).join('\n')
  const blob = new Blob([data], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'mailbox_links.csv'
  a.click()
}

onMounted(() => {
  loadMailboxes()
})
</script>
```

---

## 任务 3：前端邮箱查看页开发（Inbox.vue）

**文件位置：** `frontend/src/views/Inbox.vue`

### 功能需求

1. **JWT 验证**
   - 从 URL 参数获取 JWT token
   - 验证 token 并显示邮箱信息
   - 验证失败显示错误提示

2. **邮件列表**
   - 显示邮件列表（主题、发件人、时间）
   - 分页加载
   - 点击查看详情

3. **邮件详情**
   - 显示完整邮件内容（HTML 渲染）
   - 显示发件人、收件人、时间
   - 标记已读

### UI 设计参考

```
┌─────────────────────────────────────────────────────────┐
│  📧 test@outlook.com 的邮箱                              │
├─────────────────────────────────────────────────────────┤
│  邮件列表：                                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ ● 验证码：123456                                │    │
│  │   noreply@example.com  |  2026-05-31 10:30    │    │
│  ├────────────────────────────────────────────────┤    │
│  │ ○ Welcome to our service                       │    │
│  │   support@company.com  |  2026-05-30 15:20    │    │
│  └────────────────────────────────────────────────┘    │
│  [上一页] 1 / 5 [下一页]                                 │
│                                                          │
│  邮件详情：                                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ 主题：验证码：123456                            │    │
│  │ 发件人：noreply@example.com                    │    │
│  │ 时间：2026-05-31 10:30:00                      │    │
│  │                                                 │    │
│  │ 您的验证码是：123456                            │    │
│  │ 有效期 5 分钟。                                 │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 核心代码结构

```vue
<template>
  <n-space vertical v-if="verified">
    <n-card :title="`📧 ${mailboxInfo.email} 的邮箱`">
      <!-- 邮件列表 -->
      <n-list bordered>
        <n-list-item
          v-for="email in emails"
          :key="email.id"
          @click="selectEmail(email.id)"
          style="cursor: pointer"
        >
          <n-thing>
            <template #header>
              {{ email.is_read ? '○' : '●' }} {{ email.subject }}
            </template>
            <template #description>
              {{ email.sender }} | {{ formatDate(email.date) }}
            </template>
          </n-thing>
        </n-list-item>
      </n-list>

      <!-- 分页 -->
      <n-pagination
        v-model:page="page"
        :page-count="totalPages"
        @update:page="loadEmails"
      />

      <!-- 邮件详情 -->
      <n-card v-if="selectedEmail" title="邮件详情" style="margin-top: 20px">
        <p><strong>主题：</strong>{{ selectedEmail.subject }}</p>
        <p><strong>发件人：</strong>{{ selectedEmail.sender }}</p>
        <p><strong>时间：</strong>{{ formatDate(selectedEmail.date) }}</p>
        <n-divider />
        <div v-html="selectedEmail.body_html || selectedEmail.body_text"></div>
      </n-card>
    </n-card>
  </n-space>

  <n-result v-else status="error" title="访问链接无效或已过期" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const verified = ref(false)
const mailboxInfo = ref({ email: '' })
const emails = ref([])
const selectedEmail = ref(null)
const page = ref(1)
const totalPages = ref(1)
const jwt = ref('')

// 验证 JWT
async function verifyJWT() {
  jwt.value = route.query.jwt as string
  
  if (!jwt.value) {
    return
  }

  try {
    const response = await axios.get('/api/inbox/verify', {
      params: { jwt: jwt.value }
    })
    mailboxInfo.value = response.data
    verified.value = true
    loadEmails()
  } catch (error) {
    verified.value = false
  }
}

// 加载邮件列表
async function loadEmails() {
  try {
    const response = await axios.get('/api/inbox/emails', {
      params: {
        jwt: jwt.value,
        page: page.value,
        page_size: 20
      }
    })
    emails.value = response.data.items
    totalPages.value = Math.ceil(response.data.total / 20)
  } catch (error) {
    console.error('加载邮件失败', error)
  }
}

// 选择邮件
async function selectEmail(emailId: number) {
  try {
    const response = await axios.get(`/api/inbox/emails/${emailId}`, {
      params: { jwt: jwt.value }
    })
    selectedEmail.value = response.data
  } catch (error) {
    console.error('加载邮件详情失败', error)
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  verifyJWT()
})
</script>
```

---

## 任务 4：数据库迁移

由于添加了 `jwt_token` 字段，需要更新数据库：

```bash
# 方法 1：删除旧数据库（开发环境）
rm data/emails.db
python backend/main.py  # 自动创建新表

# 方法 2：手动添加字段（生产环境）
sqlite3 data/emails.db
ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);
CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);
```

---

## 任务 5：测试流程

### 5.1 后端测试

```bash
# 1. 安装依赖
cd backend
pip install pyjwt==2.9.0

# 2. 启动服务
python main.py

# 3. 导入邮箱
curl -X POST "http://localhost:7892/api/admin/mailboxes/import" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "mailboxes": [
      {"email": "test@outlook.com", "imap_token": "app_password_here"}
    ]
  }'

# 4. 获取邮箱链接
curl "http://localhost:7892/api/admin/mailboxes/1/link" -u admin:admin123

# 5. 验证 JWT
curl "http://localhost:7892/api/inbox/verify?jwt=YOUR_JWT_TOKEN"

# 6. 获取邮件列表
curl "http://localhost:7892/api/inbox/emails?jwt=YOUR_JWT_TOKEN&page=1"
```

### 5.2 前端测试

```bash
# 1. 启动前端
cd frontend
npm run dev

# 2. 访问管理后台
http://localhost:5173/admin

# 3. 导入邮箱并复制链接

# 4. 访问邮箱链接
http://localhost:5173/?jwt=YOUR_JWT_TOKEN
```

---

## 交付标准

### 后端完成标准

- [ ] JWT 工具类正常工作
- [ ] 导入邮箱时自动生成 JWT token
- [ ] 可以获取单个邮箱的访问链接
- [ ] 可以批量获取所有邮箱链接
- [ ] JWT 验证接口正常工作
- [ ] 邮件列表和详情接口正常工作

### 前端完成标准

- [ ] Admin.vue 可以导入邮箱
- [ ] Admin.vue 显示邮箱列表和链接
- [ ] Admin.vue 可以复制链接
- [ ] Admin.vue 可以导出所有链接
- [ ] Inbox.vue 可以验证 JWT
- [ ] Inbox.vue 显示邮件列表
- [ ] Inbox.vue 可以查看邮件详情
- [ ] 邮件详情支持 HTML 渲染

---

## 注意事项

1. **安全性**
   - JWT secret_key 必须保密
   - 生产环境修改 admin 密码
   - JWT 有效期设置为 1 年

2. **性能**
   - 邮件列表分页加载
   - 避免一次加载所有邮件

3. **用户体验**
   - 复制链接后显示提示
   - 加载时显示 loading 状态
   - 错误时显示友好提示

4. **兼容性**
   - 支持 HTML 邮件渲染
   - 支持纯文本邮件显示

---

## 参考资料

- **后端 API 文档：** docs/API_DOCUMENTATION.md
- **前端开发任务：** docs/FRONTEND_DEV_TASK.md
- **JWT 库文档：** https://pyjwt.readthedocs.io/
- **Naive UI 文档：** https://www.naiveui.com/

---

**预计开发时间：** 6-8 小时
**优先级：** 高
**难度：** 中等
