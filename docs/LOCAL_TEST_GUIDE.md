# 本地测试指南

## 当前状态
✅ 后端服务已启动  
✅ 端口：http://localhost:8000  
✅ API 文档：http://localhost:8000/docs

---

## 测试步骤

### 1. 查看 API 文档
在浏览器打开：
```
http://localhost:8000/docs
```

你会看到所有可用的 API 接口。

---

### 2. 测试健康检查
```bash
curl http://localhost:8000/health
```

**预期响应：**
```json
{"status":"ok"}
```

---

### 3. 创建 API Key（白名单）

```bash
curl -X POST "http://localhost:8000/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"test-key\",\"description\":\"测试用\",\"rate_limit\":0}"
```

**预期响应：**
```json
{
  "id": 1,
  "api_key": "sk_xxxxxxxxxxxxxxxxx",
  "name": "test-key",
  "description": "测试用",
  "rate_limit": 0,
  "is_active": true,
  "created_at": "2026-05-31T...",
  "last_used": null,
  "usage_count": 0
}
```

**⚠️ 重要：** 复制返回的 `api_key`，后面会用到！

---

### 4. 查看 API Key 列表

```bash
curl "http://localhost:8000/api/admin/api-keys" -u admin:admin123
```

**预期响应：**
```json
{
  "items": [
    {
      "id": 1,
      "api_key": "sk_xxxxxxxxxxxxxxxxx",
      "name": "test-key",
      "rate_limit": 0,
      "is_active": true,
      "created_at": "2026-05-31T...",
      "last_used": null,
      "usage_count": 0
    }
  ],
  "total": 1
}
```

---

### 5. 测试获取邮件 API（无 API Key）

```bash
curl "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=test123&num=1&boxType=1"
```

**预期响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [],
  "error": null
}
```

**说明：** 
- `data` 为空是因为邮箱不存在或密码错误
- 但 API 正常工作
- 这个请求会计入速率限制（20次/分钟）

---

### 6. 测试获取邮件 API（带 API Key）

```bash
# 替换 YOUR_API_KEY 为步骤 3 中获取的 api_key
curl "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=test123&num=1&boxType=1&api_key=YOUR_API_KEY"
```

**预期响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [],
  "error": null
}
```

**说明：** 
- 带 API Key 的请求不受速率限制
- 适合批量调用

---

### 7. 测试真实邮箱（需要应用密码）

**前提：** 你需要先生成应用密码（参考 `HOW_TO_GET_APP_PASSWORD.md`）

```bash
# 替换为你的真实邮箱和应用密码
curl "http://localhost:8000/api/GetLastEmails?email=your@outlook.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

**预期响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "Date": "2026-05-31 10:30:00",
      "From": "Sender <sender@example.com>",
      "To": "You <your@outlook.com>",
      "Subject": "邮件主题",
      "Body": "<html>完整的 HTML 内容</html>",
      "BodyPreview": "邮件预览文本...",
      "HasAttachments": false,
      "IsRead": false
    }
  ]
}
```

**说明：**
- `Date` - 邮件接收时间
- `Body` - 完整的 HTML 内容（可以在浏览器渲染）
- `BodyPreview` - 纯文本预览

---

### 8. 测试速率限制

快速发送多次请求（不带 API Key）：

```bash
# 发送 25 次请求
for i in {1..25}; do
  curl -s "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=test&num=1" | grep -o '"code":[0-9]*'
done
```

**预期结果：**
- 前 20 次：`"code":200`
- 后 5 次：`"code":429`（请求过于频繁）

**说明：** 如果间隔太长，可能不会触发限流。

---

## 使用场景示例

### 场景 1：接收验证码

```bash
# 获取最新 1 封邮件
curl "http://localhost:8000/api/GetLastEmails?email=your@outlook.com&password=YOUR_APP_PASSWORD&num=1&boxType=1"

# 从响应的 Subject 或 Body 中提取验证码
# 例如：Subject: "验证码：123456"
```

### 场景 2：查看邮件完整内容

```bash
# 获取最新 5 封邮件
curl "http://localhost:8000/api/GetLastEmails?email=your@outlook.com&password=YOUR_APP_PASSWORD&num=5&boxType=1"

# 使用 Body 字段获取完整 HTML 内容
# 可以保存到文件并在浏览器打开
```

### 场景 3：批量获取邮件（白名单）

```bash
# 使用 API Key，无速率限制
for email in email1@outlook.com email2@outlook.com email3@outlook.com; do
  curl "http://localhost:8000/api/GetLastEmails?email=${email}&password=APP_PASSWORD&num=5&api_key=YOUR_API_KEY"
done
```

---

## 常见问题

### Q1: 返回 401 错误？
**原因：** 邮箱密码错误或未使用应用密码

**解决：**
1. 确认使用的是应用密码（不是普通密码）
2. 参考 `HOW_TO_GET_APP_PASSWORD.md` 生成应用密码

### Q2: 返回 429 错误？
**原因：** 超过速率限制（20次/分钟）

**解决：**
1. 等待 1 分钟后重试
2. 或使用 API Key（白名单无限制）

### Q3: data 为空？
**原因：** 邮箱中没有邮件，或邮箱不存在

**解决：**
1. 确认邮箱地址正确
2. 确认邮箱中有邮件
3. 尝试获取垃圾箱邮件（`boxType=2`）

### Q4: 如何修改端口为 7892？
**原因：** 配置文件修改了但 uvicorn 使用了默认端口

**解决：**
```bash
# 方法 1：直接指定端口
cd backend
uvicorn main:app --host 0.0.0.0 --port 7892

# 方法 2：修改 main.py 最后几行
# 将 port=settings.port 改为 port=7892
```

---

## 下一步

### 1. 生成应用密码
参考 `HOW_TO_GET_APP_PASSWORD.md`，为你的 Outlook/Hotmail 邮箱生成应用密码。

### 2. 测试真实邮件获取
使用真实邮箱和应用密码测试步骤 7。

### 3. 前端开发
把 `FRONTEND_DEV_TASK.md` 交给 DeepSeek 开发前端 UI。

### 4. 部署到服务器
参考 `GUIDE.md` 部署到 1H1G 服务器。

---

## 快速命令汇总

```bash
# 健康检查
curl http://localhost:8000/health

# 创建 API Key
curl -X POST "http://localhost:8000/api/admin/api-keys" \
  -u admin:admin123 \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"my-key\",\"rate_limit\":0}"

# 获取邮件（无 API Key）
curl "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=test&num=1"

# 获取邮件（带 API Key）
curl "http://localhost:8000/api/GetLastEmails?email=test@outlook.com&password=test&num=1&api_key=YOUR_API_KEY"

# 查看 API 文档
浏览器打开：http://localhost:8000/docs
```

---

**当前服务状态：** ✅ 运行中  
**端口：** 8000  
**API 文档：** http://localhost:8000/docs

**开始测试吧！** 🚀
