"""
IMAP 方式测试脚本 - 使用应用密码
"""
import asyncio
import sys
sys.path.insert(0, 'D:/DevSpace/H01_hotmail_reg/imap/backend')

from services.imap_service import IMAPService


async def test_imap_with_app_password():
    """测试 IMAP 连接和邮件获取"""

    print("=" * 60)
    print("IMAP 邮件获取测试")
    print("=" * 60)

    # 你的邮箱信息
    email = "vsqamnadrz@hotmail.com"
    password = "xmcxihrzoszn80"  # 这个需要替换为应用密码

    print(f"\n邮箱: {email}")
    print(f"密码: {'*' * len(password)}")

    print("\n提示：如果使用普通密码失败，需要生成应用密码：")
    print("1. 访问 https://account.microsoft.com/security")
    print("2. 启用两步验证")
    print("3. 创建应用密码")
    print("=" * 60)

    try:
        # 测试收件箱
        print("\n[测试 1] 获取收件箱最新 2 封邮件...")
        async with IMAPService(email, password) as imap_service:
            emails = await imap_service.get_last_emails(num=2, box_type=1)

            if emails:
                print(f"✅ 成功获取 {len(emails)} 封邮件\n")
                for i, email_item in enumerate(emails, 1):
                    print(f"--- 邮件 {i} ---")
                    print(f"日期: {email_item['Date']}")
                    print(f"发件人: {email_item['From']}")
                    print(f"收件人: {email_item['To']}")
                    print(f"主题: {email_item['Subject']}")
                    print(f"预览: {email_item['BodyPreview'][:100]}...")
                    print(f"有附件: {email_item['HasAttachments']}")
                    print()
            else:
                print("⚠️ 收件箱为空或无法获取邮件")

        # 测试垃圾箱
        print("\n[测试 2] 获取垃圾箱最新 1 封邮件...")
        async with IMAPService(email, password) as imap_service:
            emails = await imap_service.get_last_emails(num=1, box_type=2)

            if emails:
                print(f"✅ 成功获取 {len(emails)} 封邮件\n")
                for i, email_item in enumerate(emails, 1):
                    print(f"--- 邮件 {i} ---")
                    print(f"日期: {email_item['Date']}")
                    print(f"主题: {email_item['Subject']}")
                    print()
            else:
                print("⚠️ 垃圾箱为空或无法获取邮件")

        print("\n" + "=" * 60)
        print("✅ IMAP 测试成功！")
        print("=" * 60)
        print("\n现在可以使用 API 接口：")
        print(f'curl "http://localhost:8000/api/GetLastEmails?email={email}&password={password}&num=2&boxType=1"')
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ IMAP 测试失败")
        print("=" * 60)
        print(f"错误: {str(e)}")

        if "AUTHENTICATE failed" in str(e) or "LOGIN failed" in str(e):
            print("\n可能的原因：")
            print("1. 使用了普通密码而非应用密码")
            print("2. 邮箱未启用 IMAP 访问")
            print("3. 密码错误")
            print("\n解决方案：")
            print("1. 访问 https://account.microsoft.com/security")
            print("2. 启用两步验证")
            print("3. 创建应用密码（格式类似：abcd-efgh-ijkl-mnop）")
            print("4. 使用应用密码替换普通密码")

        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n注意：Outlook/Hotmail 需要使用应用密码进行 IMAP 认证")
    print("如果测试失败，请按照提示生成应用密码\n")

    result = asyncio.run(test_imap_with_app_password())

    if not result:
        print("\n" + "=" * 60)
        print("下一步操作：")
        print("=" * 60)
        print("1. 生成应用密码")
        print("2. 修改此脚本中的 password 变量")
        print("3. 重新运行测试")
        sys.exit(1)
