"""
测试脚本：测试 Microsoft Graph API 和 IMAP 两种方式
"""
import asyncio
import sys
sys.path.insert(0, 'D:/DevSpace/H01_hotmail_reg/imap/backend')

from services.token_manager import TokenManager
from services.microsoft_graph import MicrosoftGraphClient


async def test_graph_api():
    """测试 Microsoft Graph API 方式"""
    print("=" * 60)
    print("测试 Microsoft Graph API 方式")
    print("=" * 60)

    # 测试凭证
    email = "vsqamnadrz@hotmail.com"
    password = "xmcxihrzoszn80"
    client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    refresh_token = "M.C552_SN1.0.U.-Cte62KcUKkmHewOGkCKsLkUVj*sZqv*UtGMAoWTWNybpXjPqvWn3Qc9pFwEFtI5hKLUS4X*jyqwFdapiK6szgNlMINaQqUVPg10GB8gwzEofaeVNBnNXBdzQhARZMlxjblbz7FKIaJ62yCcKixRYXyiQLDKZBp2qglLrpggRdjkhQuel2syRCfA3O2g!c7ozP!R4BBC1lGASqjHlH19rH1ZF3RCJrpDLr2AWAuZ5msLNz8*6SX0X9!iJvdxW374Q!8k6Fq7SuaxiuoebZBrIum79ShjfqBx*S8qo*9Fz2*!JA*zOegjEQU9HYAwhQI55HXRAA3MNE1VfL*ijKccaJI5o1uLbwT0YT13X6*h3MdWqDr*j5Xzybz91vrBykNM4Qyg2pWCCDfq*dHoxRParkycFbkQNxqa*wEnaG0pys*8Te75E4qaLGy9tgDxhsQtD*g$$"

    print(f"\n邮箱: {email}")
    print(f"客户端ID: {client_id}")
    print(f"刷新令牌: {refresh_token[:50]}...")

    # 步骤 1: 获取 access token
    print("\n步骤 1: 获取 Access Token...")
    token_manager = TokenManager()
    access_token = await token_manager.get_access_token(
        client_id=client_id,
        refresh_token=refresh_token,
        email=email
    )

    if not access_token:
        print("❌ 获取 Access Token 失败")
        print("\n可能的原因：")
        print("1. refresh_token 已过期")
        print("2. client_id 不正确")
        print("3. 网络连接问题")
        return False

    print(f"✅ 成功获取 Access Token: {access_token[:50]}...")

    # 步骤 2: 获取收件箱邮件
    print("\n步骤 2: 获取收件箱最新 2 封邮件...")
    graph_client = MicrosoftGraphClient(access_token)
    emails = await graph_client.get_last_emails(
        email=email,
        num=2,
        box_type=1
    )

    if emails:
        print(f"✅ 成功获取 {len(emails)} 封邮件")
        for i, email_item in enumerate(emails, 1):
            print(f"\n邮件 {i}:")
            print(f"  日期: {email_item['Date']}")
            print(f"  发件人: {email_item['From']}")
            print(f"  收件人: {email_item['To']}")
            print(f"  主题: {email_item['Subject']}")
            print(f"  预览: {email_item['BodyPreview'][:100]}...")
            print(f"  有附件: {email_item['HasAttachments']}")
            print(f"  已读: {email_item['IsRead']}")
        return True
    else:
        print("❌ 未获取到邮件")
        return False


async def test_imap():
    """测试 IMAP 方式"""
    print("\n" + "=" * 60)
    print("测试 IMAP 方式")
    print("=" * 60)

    import aioimaplib

    email = "vsqamnadrz@hotmail.com"
    password = "xmcxihrzoszn80"

    print(f"\n邮箱: {email}")
    print(f"密码: {password}")

    try:
        print("\n步骤 1: 连接到 IMAP 服务器...")
        imap_client = aioimaplib.IMAP4_SSL(host="outlook.office365.com", port=993)
        await imap_client.wait_hello_from_server()
        print("✅ 成功连接到服务器")

        print("\n步骤 2: 登录...")
        response = await imap_client.login(email, password)
        print(f"登录响应: {response}")

        if response.result == "OK":
            print("✅ 登录成功")

            print("\n步骤 3: 选择收件箱...")
            await imap_client.select("INBOX")
            print("✅ 成功选择收件箱")

            print("\n步骤 4: 搜索最新邮件...")
            _, msg_ids = await imap_client.search("ALL")
            msg_id_list = msg_ids[0].split()

            if msg_id_list:
                latest_ids = msg_id_list[-2:]  # 最新 2 封
                print(f"✅ 找到 {len(latest_ids)} 封邮件")

                for msg_id in latest_ids:
                    print(f"\n获取邮件 ID: {msg_id.decode()}...")
                    _, msg_data = await imap_client.fetch(msg_id, "(RFC822)")
                    print(f"邮件数据长度: {len(msg_data[1])} 字节")
            else:
                print("❌ 收件箱为空")

            await imap_client.logout()
            return True
        else:
            print(f"❌ 登录失败: {response}")
            return False

    except Exception as e:
        print(f"❌ IMAP 测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("邮件获取方式对比测试")
    print("=" * 60)

    # 测试 Graph API
    graph_success = await test_graph_api()

    # 测试 IMAP
    imap_success = await test_imap()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"Microsoft Graph API: {'✅ 成功' if graph_success else '❌ 失败'}")
    print(f"IMAP: {'✅ 成功' if imap_success else '❌ 失败'}")

    print("\n推荐方案：")
    if graph_success:
        print("✅ 使用 Microsoft Graph API")
        print("   优点：")
        print("   - 速度快，响应时间短")
        print("   - 支持收件箱和垃圾箱")
        print("   - OAuth2 认证更安全")
        print("   - 返回格式化的邮件数据")
    elif imap_success:
        print("✅ 使用 IMAP")
        print("   优点：")
        print("   - 标准协议，兼容性好")
        print("   - 不需要 Azure AD 应用")
        print("   缺点：")
        print("   - 需要解析原始邮件格式")
        print("   - 连接开销较大")
    else:
        print("❌ 两种方式都失败，请检查凭证")


if __name__ == "__main__":
    asyncio.run(main())
