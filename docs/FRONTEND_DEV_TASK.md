# 邮件托管系统前端开发任务

## 项目背景

这是一个轻量级的 Outlook/Hotmail 邮件托管系统，后端已完成 90%，使用 FastAPI + IMAP 实现。现在需要完成前端 UI 开发。

**项目路径：** `D:\DevSpace\H01_hotmail_reg\imap`

**技术栈：**
- 后端：FastAPI + aioimaplib + SQLite
- 前端：Vue 3 + TypeScript + Naive UI + Vite

**后端服务地址：** `http://localhost:7892`

---

## 你的任务

完成两个前端页面的开发：
1. **Admin.vue** - 管理员面板（批量导入和管理邮箱）
2. **Inbox.vue** - 用户邮件面板（查看邮件列表和详情）

---

## 开始前的准备

### 1. 阅读项目文档

先阅读以下文件了解项目结构和 API：
- `README.md` - 项目概览
- `GUIDE.md` - 完整使用指南（重点看 API 接口部分）
- `frontend/src/utils/api.ts` - API 客户端封装

### 2. 查看现有代码

- `backend/routers/admin.py` - 管理员 API 接口
- `backend/routers/emails.py` - 邮件 API 接口
- `backend/models.py` - 数据模型定义
- `frontend/src/router/index.ts` - 路由配置

### 3. 启动后端服务

```bash
cd backend
python main.py
# 后端运行在 http://localhost:7892
# API 文档：http://localhost:7892/docs
```

---

## 任务 1：实现 Admin.vue（管理员面板）

**路由：** `/admin`

**功能需求：**

### 1.1 批量导入邮箱
- 提供一个多行文本框，支持批量输入邮箱信息
- 格式：每行一个邮箱，格式为 `email,password`
- 示例：
  ```
  user1@outlook.com,app-password-1
  user2@hotmail.com,app-password-2
  ```
- 点击"导入"按钮后调用 API：`POST /api/admin/mailboxes/import`
- 请求体格式：
  ```json
  {
    "mailboxes": [
      {
        "email": "user1@outlook.com",
        "imap_token": "app-password-1"
      }
    ]
  }
  ```
- 显示导入结果（成功数量、失败数量、错误信息）

### 1.2 邮箱列表管理
- 显示所有已导入的邮箱列表（表格形式）
- 表格列：
  - 邮箱地址
  - 同步状态（最后同步时间）
  - 邮件数量
  - 操作按钮（删除）
- 支持分页（每页 20 条）
- 调用 API：`GET /api/admin/mailboxes?page=1&page_size=20`
- 响应格式：
  ```json
  {
    "items": [
      {
        "id": 1,
        "email": "user@outlook.com",
        "last_sync": "2026-05-31T10:30:00",
        "email_count": 150,
        "is_active": true
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
  ```

### 1.3 删除邮箱
- 点击删除按钮时弹出确认对话框
- 确认后调用 API：`DELETE /api/admin/mailboxes/{id}`
- 删除成功后刷新列表

### UI 设计要求
- 使用 Naive UI 的 `n-card`、`n-data-table`、`n-input`、`n-button`、`n-modal` 等组件
- 布局清晰，左侧是导入区域，右侧是列表区域（或上下布局）
- 添加加载状态（loading）和错误提示（message）
- 响应式设计，适配不同屏幕尺寸

---

## 任务 2：实现 Inbox.vue（用户邮件面板）

**路由：** `/inbox`

**功能需求：**

### 2.1 邮箱选择器
- 顶部显示一个下拉选择器，列出所有可用邮箱
- 调用 API：`GET /api/admin/mailboxes?page=1&page_size=1000`
- 选择邮箱后，加载该邮箱的邮件列表

### 2.2 邮件列表
- 左侧显示邮件列表（或顶部显示）
- 每个邮件项显示：
  - 发件人
  - 主题
  - 接收时间
  - 未读状态（未读邮件加粗或高亮）
- 调用 API：`GET /api/emails/?mailbox_id={id}&page=1&page_size=20`
- 响应格式：
  ```json
  {
    "items": [
      {
        "id": 1,
        "subject": "Welcome",
        "sender": "noreply@microsoft.com",
        "received_at": "2026-05-31T10:30:00",
        "is_read": false,
        "has_attachments": false
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
  ```
- 支持分页

### 2.3 邮件详情
- 点击邮件列表中的某封邮件，右侧（或下方）显示详情
- 调用 API：`GET /api/emails/{id}`
- 响应格式：
  ```json
  {
    "id": 1,
    "subject": "Welcome",
    "sender": "noreply@microsoft.com",
    "sender_name": "Microsoft Team",
    "received_at": "2026-05-31T10:30:00",
    "body_html": "<html>...</html>",
    "body_text": "Plain text...",
    "is_read": false,
    "has_attachments": false,
    "attachments": []
  }
  ```
- 显示内容：
  - 发件人（名称 + 邮箱）
  - 收件人
  - 主题
  - 接收时间
  - 邮件正文（HTML 渲染，注意安全性）
  - 附件列表（如果有）

### 2.4 标记已读
- 打开邮件详情时，自动调用 API 标记为已读
- 调用 API：`PUT /api/emails/{id}/read`
- 更新列表中的未读状态

### 2.5 手动刷新
- 添加一个"刷新"按钮，手动触发邮件同步
- 调用 API：`POST /api/emails/refresh?mailbox_id={id}`
- 刷新成功后重新加载邮件列表

### 2.6 快捷复制邮箱地址
- 在邮箱选择器旁边添加一个复制按钮（📋 图标）
- 点击后复制当前选中的邮箱地址到剪贴板
- 显示"已复制"提示

### UI 设计要求
- 使用 Naive UI 的 `n-layout`、`n-layout-sider`、`n-list`、`n-card`、`n-select` 等组件
- 左右分栏布局（或上下布局）：左侧邮件列表，右侧邮件详情
- 未读邮件用粗体或不同颜色标识
- 邮件正文使用 `v-html` 渲染（注意 XSS 防护）
- 添加加载状态和空状态提示
- 响应式设计

---

## 技术要求

### 1. API 调用
- 使用 `frontend/src/utils/api.ts` 中封装的 API 客户端
- 如果没有封装，使用 `axios` 或 `fetch` 调用后端 API
- 后端地址：`http://localhost:7892`
- 处理错误情况（网络错误、API 错误、超时等）

### 2. 状态管理
- 可以使用 Vue 3 的 `ref`、`reactive` 进行组件内状态管理
- 如果需要跨组件共享状态，可以使用 `provide/inject` 或 Pinia

### 3. 类型定义
- 使用 TypeScript 定义接口类型
- 为 API 响应数据定义类型
- 示例：
  ```typescript
  interface Mailbox {
    id: number;
    email: string;
    last_sync: string;
    email_count: number;
    is_active: boolean;
  }

  interface Email {
    id: number;
    subject: string;
    sender: string;
    received_at: string;
    is_read: boolean;
    has_attachments: boolean;
  }
  ```

### 4. 错误处理
- 使用 Naive UI 的 `useMessage` 显示成功/错误提示
- 使用 `useDialog` 显示确认对话框
- 网络错误时显示友好的错误信息

### 5. 性能优化
- 邮件列表使用虚拟滚动（如果数据量大）
- 邮件详情懒加载（点击时才加载）
- 避免不必要的 API 重复调用

### 6. 安全性
- 邮件正文 HTML 渲染时防止 XSS 攻击
- 可以使用 `DOMPurify` 库清理 HTML
- 或者使用 `<iframe sandbox>` 隔离渲染

---

## 开发步骤建议

### 第 1 步：搭建基础框架
1. 创建 `Admin.vue` 和 `Inbox.vue` 文件
2. 配置路由（如果还没配置）
3. 添加基础布局和导航

### 第 2 步：实现 Admin.vue
1. 先实现邮箱列表展示（调用 API，渲染表格）
2. 再实现批量导入功能（文本框 + 解析 + API 调用）
3. 最后实现删除功能（确认对话框 + API 调用）
4. 测试所有功能

### 第 3 步：实现 Inbox.vue
1. 先实现邮箱选择器（下拉框 + API 调用）
2. 再实现邮件列表展示（左侧列表 + 分页）
3. 然后实现邮件详情展示（右侧详情 + HTML 渲染）
4. 添加标记已读功能（自动调用 API）
5. 添加手动刷新和复制功能
6. 测试所有功能

### 第 4 步：优化和测试
1. 添加加载状态和错误处理
2. 优化 UI 样式和交互
3. 测试边界情况（空数据、网络错误、大量数据等）
4. 响应式适配

---

## 测试数据

### 测试邮箱导入
可以使用以下格式测试导入功能：
```
test1@outlook.com,password1
test2@hotmail.com,password2
```

### 测试 API
启动后端后，可以在浏览器访问：
- API 文档：http://localhost:7892/docs
- 测试接口：直接在 Swagger UI 中测试

---

## 注意事项

1. **IMAP 认证问题**
   - Outlook/Hotmail 需要使用应用密码，不能用普通密码
   - 如果测试时遇到认证失败，参考 `HOW_TO_GET_APP_PASSWORD.md`

2. **CORS 问题**
   - 后端已配置 CORS，允许所有来源
   - 如果遇到跨域问题，检查后端 `main.py` 的 CORS 配置

3. **数据库初始化**
   - 首次启动后端时会自动创建数据库
   - 数据库文件：`data/emails.db`

4. **前端开发服务器**
   - 运行 `npm run dev` 启动前端
   - 默认端口：http://localhost:5173

5. **端口配置**
   - 后端端口已修改为 7892（避免冲突）
   - 配置文件：`backend/config.py`

---

## 交付标准

完成后，应满足以下标准：

✅ Admin.vue 可以批量导入邮箱  
✅ Admin.vue 可以查看和删除邮箱  
✅ Inbox.vue 可以选择邮箱并查看邮件列表  
✅ Inbox.vue 可以查看邮件详情（HTML 正文正常渲染）  
✅ 点击邮件自动标记为已读  
✅ 可以手动刷新邮件  
✅ 可以快捷复制邮箱地址  
✅ 所有 API 调用都有错误处理  
✅ UI 美观，交互流畅  
✅ 代码使用 TypeScript，类型定义完整

---

## 参考资源

- **Naive UI 文档：** https://www.naiveui.com/
- **Vue 3 文档：** https://vuejs.org/
- **FastAPI 文档：** https://fastapi.tiangolo.com/
- **项目 API 文档：** http://localhost:7892/docs（启动后端后访问）

---

## 预计工作量

- Admin.vue：2-3 小时
- Inbox.vue：3-4 小时
- 测试和优化：1-2 小时
- **总计：6-9 小时**

---

## 快速命令

```bash
# 启动后端
cd backend
python main.py
# 访问 http://localhost:7892/docs

# 启动前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173

# 测试 API
curl "http://localhost:7892/api/GetLastEmails?email=test@outlook.com&password=APP_PASSWORD&num=2&boxType=1"
```

---

## 开始开发

现在请按照以上要求开始开发。如果遇到问题，可以：
1. 查看后端 API 文档（http://localhost:7892/docs）
2. 阅读项目文档（README.md、GUIDE.md）
3. 检查现有代码（backend/routers/、backend/models.py）

祝开发顺利！
