# 如何为 Outlook/Hotmail 生成应用密码

## 问题说明

你的邮箱 `vsqamnadrz@hotmail.com` 使用普通密码 `xmcxihrzoszn80` 无法通过 IMAP 认证。

**错误信息：** `AUTHENTICATE failed`

**原因：** Microsoft 要求使用**应用密码**进行 IMAP 认证，而不是普通密码。

---

## 解决方案：生成应用密码

### 步骤 1：启用两步验证

1. 访问 [Microsoft 账户安全设置](https://account.microsoft.com/security)
2. 使用你的邮箱 `vsqamnadrz@hotmail.com` 登录
3. 找到 **"高级安全选项"** 或 **"Additional security options"**
4. 点击 **"两步验证"** 或 **"Two-step verification"**
5. 点击 **"启用"** 或 **"Turn on"**
6. 按照提示完成设置（可能需要验证手机号或备用邮箱）

### 步骤 2：生成应用密码

1. 在同一页面（安全设置），找到 **"应用密码"** 或 **"App passwords"**
2. 点击 **"创建新的应用密码"** 或 **"Create a new app password"**
3. 输入名称（例如：`IMAP API`）
4. 点击 **"创建"** 或 **"Create"**
5. **重要：** 复制生成的密码（格式类似：`abcd-efgh-ijkl-mnop`）
6. 这个密码只显示一次，请妥善保存

### 步骤 3：使用应用密码测试

1. 打开 `test_imap_simple.py` 文件
2. 将第 13 行的密码替换为应用密码：
   ```python
   password = "abcd-efgh-ijkl-mnop"  # 替换为你的应用密码
   ```
3. 运行测试：
   ```bash
   python test_imap_simple.py
   ```

### 步骤 4：使用 API

如果测试成功，就可以使用 API 了：

```bash
# 启动服务
python main.py

# 测试 API
curl "http://localhost:8000/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

---

## 常见问题

### Q1: 找不到"应用密码"选项？

**A:** 必须先启用两步验证，才能看到应用密码选项。

### Q2: 两步验证会影响正常登录吗？

**A:** 不会。两步验证只在新设备登录时需要额外验证，日常使用不受影响。

### Q3: 应用密码忘记了怎么办？

**A:** 应用密码无法查看，只能删除旧的，重新生成新的。

### Q4: 可以使用普通密码吗？

**A:** 不可以。Microsoft 已经禁用了 IMAP 的基本身份验证（用户名+密码），必须使用应用密码。

---

## 备选方案：如果无法生成应用密码

如果你的账户无法启用两步验证或生成应用密码，可以考虑：

1. **使用 Microsoft Graph API**
   - 需要创建 Azure AD 应用
   - 使用 OAuth2 认证
   - 参考 `DEVELOPER_GUIDE.md` 中的 Graph API 方式

2. **使用其他邮箱**
   - 如果有其他支持 IMAP 的邮箱
   - 可以用于测试

---

## 快速参考

**Microsoft 账户安全设置：**
https://account.microsoft.com/security

**需要做的事情：**
1. ✅ 启用两步验证
2. ✅ 生成应用密码
3. ✅ 替换测试脚本中的密码
4. ✅ 运行测试
5. ✅ 使用 API

---

## 测试命令

```bash
# 1. 测试 IMAP 连接
cd backend
python test_imap_simple.py

# 2. 启动 API 服务
python main.py

# 3. 测试 API（替换 YOUR_APP_PASSWORD）
curl "http://localhost:8000/api/GetLastEmails?email=vsqamnadrz@hotmail.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

---

**重要提示：** 应用密码只显示一次，生成后请立即保存！
