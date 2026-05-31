# API 文档

## 概述

本系统提供邮件获取 API，支持实时从 Outlook/Hotmail 邮箱获取邮件内容。

**基础 URL：** `http://your-server:7892`

**认证方式：**
- 外部 API：API Key（白名单无限制，非白名单限流）
- 管理员 API：Basic Auth

---

## 1. 外部 API - 获取邮件

### 1.1 获取最新邮件

**接口：** `GET /api/GetLastEmails`

**用途：** 实时获取邮箱最新邮件，适用于接收验证码、查看邮件信息等场景

**请求参数：**

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| email | string | 是 | 邮箱地址 | `user@outlook.com` |
| password | string | 是 | 应用密码 | `abcd-efgh-ijkl-mnop` |
| num | integer | 否 | 获取数量（1-5，默认1） | `2` |
| boxType | integer | 否 | 邮箱类型（1=收件箱，2=垃圾箱，默认1） | `1` |
| api_key | string | 否 | API 密钥（白名单用户） | `your-api-key` |

**请求示例：**

```bash
# 获取收件箱最新 2 封邮件
curl "http://localhost:7892/api/GetLastEmails?email=user@outlook.com&password=app-password&num=2&boxType=1"

# 使用 API Key（白名单用户）
curl "http://localhost:7892/api/GetLastEmails?email=user@outlook.com&password=app-password&num=5&api_key=your-api-key"
```

**响应格式：**

```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "Date": "2026-05-31 10:30:00",
      "From": "Sender Name <sender@example.com>",
      "To": "Recipient <recipient@example.com>",
      "Subject": "验证码：123456",
      "Body": "<html><body>您的验证码是：123456</body></html>",
      "BodyPreview": "您的验证码是：123456",
      "HasAttachments": false,
      "IsRead": false
    }
  ]
}
```

**响应字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 状态码（200=成功，400=参数错误，401=认证失败，429=限流） |
| message | string | 响应消息 |
| data | array | 邮件列表 |
| data[].Date | string | 接收时间（格式：YYYY-MM-DD HH:MM:SS） |
| data[].From | string | 发件人（格式：名称 <邮箱>） |
| data[].To | string | 收件人 |
| data[].Subject | string | 邮件主题 |
| data[].Body | string | 邮件完整内容（HTML 格式） |
| data[].BodyPreview | string | 邮件预览（纯文本，前 200 字符） |
| data[].HasAttachments | boolean | 是否有附件 |
| data[].IsRead | boolean | 是否已读 |

**错误响应：**

```json
{
  "code": 401,
  "message": "IMAP 认证失败，请检查邮箱和密码",
  "data": []
}
```

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试（限制：20次/分钟）",
  "data": []
}
```

**速率限制：**

| 用户类型 | 限制 | 说明 |
|---------|------|------|
| 白名单用户（有 API Key） | 无限制 | 适用于批量化场景 |
| 普通用户（无 API Key） | 20次/分钟 | 适用于单次查询 |

---

### 1.2 使用场景

#### 场景 1：接收验证码

```bash
# 获取最新 1 封邮件
curl "http://localhost:7892/api/GetLastEmails?email=user@outlook.com&password=app-password&num=1&boxType=1"

# 从响应中提取验证码
# Subject: "验证码：123456"
# Body: "您的验证码是：123456"
```

#### 场景 2：查看邮件完整内容

```bash
# 获取最新 5 封邮件
curl "http://localhost:7892/api/GetLastEmails?email=user@outlook.com&password=app-password&num=5&boxType=1"

# 使用 Body 字段获取完整 HTML 内容
# 可以在浏览器中渲染显示
```

#### 场景 3：批量获取邮件（白名单用户）

```bash
# 使用 API Key，无速率限制
for email in email1 email2 email3; do
  curl "http://localhost:7892/api/GetLastEmails?email=${email}@outlook.com&password=app-password&num=5&api_key=your-api-key"
done
```

---

## 2. 管理员 API - API Key 管理

### 2.1 创建 API Key

**接口：** `POST /api/admin/api-keys`

**认证：** Basic Auth（用户名：admin，密码：admin123）

**请求体：**

```json
{
  "name": "批量任务",
  "description": "用于批量获取邮件",
  "rate_limit": 0
}
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | API Key 名称 |
| description | string | 否 | 描述 |
| rate_limit | integer | 否 | 速率限制（0=无限制，默认0） |

**响应：**

```json
{
  "id": 1,
  "api_key": "sk_1a2b3c4d5e6f7g8h9i0j",
  "name": "批量任务",
  "description": "用于批量获取邮件",
  "rate_limit": 0,
  "is_active": true,
  "created_at": "2026-05-31T10:30:00"
}
```

**请求示例：**

```bash
curl -X POST "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "批量任务",
    "description": "用于批量获取邮件",
    "rate_limit": 0
  }'
```

---

### 2.2 查看 API Key 列表

**接口：** `GET /api/admin/api-keys`

**认证：** Basic Auth

**请求示例：**

```bash
curl "http://localhost:7892/api/admin/api-keys" \
  -u admin:admin123
```

**响应：**

```json
{
  "items": [
    {
      "id": 1,
      "api_key": "sk_1a2b3c4d5e6f7g8h9i0j",
      "name": "批量任务",
      "rate_limit": 0,
      "is_active": true,
      "created_at": "2026-05-31T10:30:00",
      "last_used": "2026-05-31T12:00:00",
      "usage_count": 1523
    }
  ],
  "total": 1
}
```

---

### 2.3 删除 API Key

**接口：** `DELETE /api/admin/api-keys/{id}`

**认证：** Basic Auth

**请求示例：**

```bash
curl -X DELETE "http://localhost:7892/api/admin/api-keys/1" \
  -u admin:admin123
```

**响应：**

```json
{
  "message": "API Key 已删除"
}
```

---

### 2.4 更新速率限制

**接口：** `PUT /api/admin/api-keys/{id}`

**认证：** Basic Auth

**请求体：**

```json
{
  "rate_limit": 100,
  "is_active": true
}
```

**请求示例：**

```bash
curl -X PUT "http://localhost:7892/api/admin/api-keys/1" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "rate_limit": 100,
    "is_active": true
  }'
```

---

## 3. 速率限制规则

### 3.1 限流策略

| 用户类型 | 识别方式 | 限制 | 超限响应 |
|---------|---------|------|---------|
| 白名单用户 | 提供有效 `api_key` | 无限制（或自定义） | - |
| 普通用户 | 无 `api_key` 或无效 | 20次/分钟 | HTTP 429 |

### 3.2 限流实现

**基于 IP 地址：**
- 使用滑动窗口算法
- 统计最近 1 分钟内的请求次数
- 超过限制返回 429 错误

**白名单豁免：**
- 提供有效 `api_key` 的请求不受限制
- API Key 可以设置自定义速率限制

### 3.3 超限响应

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试（限制：20次/分钟）",
  "data": [],
  "retry_after": 45
}
```

**响应头：**
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1717142400
Retry-After: 45
```

---

## 4. 前端 UI 集成

### 4.1 管理员面板新增功能

**API Key 管理页面：**

- 显示所有 API Key 列表
- 创建新的 API Key
- 设置速率限制（0=无限制）
- 查看使用统计（调用次数、最后使用时间）
- 启用/禁用 API Key
- 删除 API Key

**UI 组件：**
- 表格显示 API Key 列表
- 创建按钮 + 表单对话框
- 复制 API Key 按钮
- 删除确认对话框

### 4.2 邮件查看页面

**显示邮件完整内容：**

```vue
<template>
  <div class="email-detail">
    <div class="email-header">
      <h3>{{ email.Subject }}</h3>
      <p>发件人：{{ email.From }}</p>
      <p>时间：{{ email.Date }}</p>
    </div>
    <div class="email-body" v-html="sanitizeHtml(email.Body)"></div>
  </div>
</template>

<script setup>
import DOMPurify from 'dompurify';

const sanitizeHtml = (html) => {
  return DOMPurify.sanitize(html);
};
</script>
```

---

## 5. 安全建议

### 5.1 应用密码安全

- ❌ 不要在 URL 中明文传输密码（使用 HTTPS）
- ✅ 使用应用密码，不要使用账户主密码
- ✅ 定期更换应用密码
- ✅ 不要在日志中记录密码

### 5.2 API Key 安全

- ✅ API Key 只显示一次，创建后立即保存
- ✅ 使用 `sk_` 前缀标识 API Key
- ✅ 定期审计 API Key 使用情况
- ✅ 及时删除不再使用的 API Key

### 5.3 HTML 渲染安全

- ✅ 使用 DOMPurify 清理 HTML
- ✅ 或使用 `<iframe sandbox>` 隔离渲染
- ❌ 不要直接使用 `v-html` 渲染未清理的内容

---

## 6. 错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 200 | 成功 | - |
| 400 | 参数错误 | 检查请求参数格式 |
| 401 | 认证失败 | 检查邮箱和应用密码 |
| 403 | 无权限 | 检查 API Key 是否有效 |
| 404 | 资源不存在 | 检查请求路径 |
| 429 | 请求过于频繁 | 等待后重试或使用 API Key |
| 500 | 服务器错误 | 联系管理员 |

---

## 7. 完整示例

### Python 示例

```python
import requests

# 配置
API_URL = "http://localhost:7892/api/GetLastEmails"
EMAIL = "user@outlook.com"
PASSWORD = "app-password"
API_KEY = "sk_1a2b3c4d5e6f7g8h9i0j"  # 可选

# 获取邮件
response = requests.get(API_URL, params={
    "email": EMAIL,
    "password": PASSWORD,
    "num": 5,
    "boxType": 1,
    "api_key": API_KEY  # 白名单用户
})

data = response.json()

if data["code"] == 200:
    for email in data["data"]:
        print(f"主题: {email['Subject']}")
        print(f"时间: {email['Date']}")
        print(f"内容: {email['BodyPreview']}")
        print("-" * 50)
else:
    print(f"错误: {data['message']}")
```

### JavaScript 示例

```javascript
// 获取邮件
async function getEmails(email, password, apiKey) {
  const url = new URL('http://localhost:7892/api/GetLastEmails');
  url.searchParams.append('email', email);
  url.searchParams.append('password', password);
  url.searchParams.append('num', 5);
  url.searchParams.append('boxType', 1);
  if (apiKey) {
    url.searchParams.append('api_key', apiKey);
  }

  const response = await fetch(url);
  const data = await response.json();

  if (data.code === 200) {
    data.data.forEach(email => {
      console.log(`主题: ${email.Subject}`);
      console.log(`时间: ${email.Date}`);
      console.log(`内容: ${email.BodyPreview}`);
      console.log('-'.repeat(50));
    });
  } else {
    console.error(`错误: ${data.message}`);
  }
}

// 使用
getEmails('user@outlook.com', 'app-password', 'sk_1a2b3c4d5e6f7g8h9i0j');
```

---

## 8. 部署检查清单

部署前确认：

- [ ] 修改管理员密码（`backend/config.py`）
- [ ] 启用 HTTPS（使用 Nginx 反向代理）
- [ ] 配置防火墙（只开放必要端口）
- [ ] 设置日志记录（记录 API 调用）
- [ ] 配置监控告警（API 错误率、响应时间）
- [ ] 测试速率限制是否生效
- [ ] 测试 API Key 认证是否正常

---

## 9. 常见问题

### Q1: 如何获取应用密码？

参考 `HOW_TO_GET_APP_PASSWORD.md` 文档。

### Q2: 为什么返回 401 错误？

检查：
1. 邮箱地址是否正确
2. 是否使用应用密码（不是普通密码）
3. 应用密码是否过期

### Q3: 如何提高请求速率？

申请 API Key，加入白名单即可无限制调用。

### Q4: 邮件内容是否安全？

邮件内容通过 HTTPS 加密传输，但建议：
1. 不要在公共网络使用
2. 使用 DOMPurify 清理 HTML
3. 不要在日志中记录敏感信息

---

**API 文档版本：** v1.0  
**最后更新：** 2026-05-31
