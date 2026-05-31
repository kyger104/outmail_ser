"""
IMAP 简单测试脚本
"""
import asyncio
import sys
sys.path.insert(0, 'D:/DevSpace/H01_hotmail_reg/imap/backend')

from services.imap_service import IMAPService


async def test_imap():
    """测试 IMAP 连接"""

    print("=" * 60)
    print("IMAP Test")
    print("=" * 60)

    # 邮箱信息
    email = "vsqamnadrz@hotmail.com"
    password = "xmcxihrzoszn80"  # 需要替换为应用密码

    print(f"\nEmail: {email}")
    print(f"Password: {'*' * len(password)}")
    print("\nNote: Outlook/Hotmail requires App Password for IMAP")
    print("=" * 60)

    try:
        print("\n[Test] Fetching last 2 emails from Inbox...")
        async with IMAPService(email, password) as imap_service:
            emails = await imap_service.get_last_emails(num=2, box_type=1)

            if emails:
                print(f"\nSuccess! Got {len(emails)} emails\n")
                for i, email_item in enumerate(emails, 1):
                    print(f"--- Email {i} ---")
                    print(f"Date: {email_item['Date']}")
                    print(f"From: {email_item['From']}")
                    print(f"Subject: {email_item['Subject']}")
                    print()
            else:
                print("\nNo emails found")

        print("=" * 60)
        print("IMAP Test SUCCESS!")
        print("=" * 60)
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("IMAP Test FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")

        if "AUTHENTICATE failed" in str(e) or "LOGIN failed" in str(e):
            print("\nPossible reasons:")
            print("1. Using normal password instead of App Password")
            print("2. IMAP not enabled for this account")
            print("3. Wrong password")
            print("\nSolution:")
            print("1. Visit https://account.microsoft.com/security")
            print("2. Enable Two-Step Verification")
            print("3. Create App Password")
            print("4. Replace password in this script")

        return False


if __name__ == "__main__":
    result = asyncio.run(test_imap())
    sys.exit(0 if result else 1)
