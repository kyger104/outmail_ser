"""
获取 Microsoft OAuth2 Refresh Token 的辅助脚本

使用方法：
1. 在 Azure Portal 创建应用注册
2. 配置 API 权限：Mail.Read, Mail.ReadWrite, offline_access
3. 运行此脚本，按照提示操作
4. 保存获取到的 refresh_token
"""
import msal
import sys


def get_refresh_token_device_flow(client_id: str):
    """
    使用设备码流程获取 refresh_token

    优点：
    - 不需要配置重定向 URI
    - 适合命令行环境
    - 用户体验友好

    Args:
        client_id: Azure AD 应用的客户端 ID
    """
    print("=" * 60)
    print("方法 1: 设备码流程（推荐）")
    print("=" * 60)

    # 创建 MSAL 应用
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority="https://login.microsoftonline.com/common"
    )

    # 启动设备码流程
    scopes = ["https://graph.microsoft.com/.default", "offline_access"]
    flow = app.initiate_device_flow(scopes=scopes)

    if "user_code" not in flow:
        print("❌ 错误：无法启动设备码流程")
        print(f"错误信息: {flow.get('error')}")
        return None

    # 显示用户需要访问的 URL 和代码
    print("\n" + "=" * 60)
    print("请按照以下步骤操作：")
    print("=" * 60)
    print(flow["message"])
    print("\n提示：")
    print("1. 在浏览器中打开上述 URL")
    print("2. 输入显示的代码")
    print("3. 使用你的 Outlook/Hotmail 账户登录")
    print("4. 授权应用访问你的邮件")
    print("5. 完成后返回此窗口")
    print("=" * 60)

    # 等待用户完成授权
    print("\n等待授权中...")
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        print("\n✅ 授权成功！")
        print("\n" + "=" * 60)
        print("获取到的令牌信息：")
        print("=" * 60)
        print(f"Access Token: {result['access_token'][:50]}...")
        print(f"Refresh Token: {result['refresh_token']}")
        print(f"Token Type: {result.get('token_type', 'Bearer')}")
        print(f"Expires In: {result.get('expires_in', 3600)} 秒")

        print("\n" + "=" * 60)
        print("重要：请保存 Refresh Token")
        print("=" * 60)
        print("将以下 Refresh Token 保存到安全的地方：")
        print(f"\n{result['refresh_token']}\n")
        print("此令牌将用于 API 调用，有效期约 90 天。")
        print("=" * 60)

        return result['refresh_token']
    else:
        print("\n❌ 授权失败")
        print(f"错误: {result.get('error')}")
        print(f"错误描述: {result.get('error_description')}")
        return None


def get_refresh_token_interactive(client_id: str):
    """
    使用交互式登录获取 refresh_token

    优点：
    - 自动打开浏览器
    - 流程简单

    缺点：
    - 需要图形界面
    - 需要配置重定向 URI

    Args:
        client_id: Azure AD 应用的客户端 ID
    """
    print("=" * 60)
    print("方法 2: 交互式登录")
    print("=" * 60)

    # 创建 MSAL 应用
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority="https://login.microsoftonline.com/common"
    )

    # 启动交互式登录
    scopes = ["https://graph.microsoft.com/.default", "offline_access"]

    print("\n浏览器将自动打开，请在浏览器中完成登录...")
    result = app.acquire_token_interactive(scopes=scopes)

    if "access_token" in result:
        print("\n✅ 授权成功！")
        print(f"\nRefresh Token: {result['refresh_token']}")
        return result['refresh_token']
    else:
        print("\n❌ 授权失败")
        print(f"错误: {result.get('error')}")
        print(f"错误描述: {result.get('error_description')}")
        return None


def test_refresh_token(client_id: str, refresh_token: str):
    """
    测试 refresh_token 是否有效

    Args:
        client_id: Azure AD 应用的客户端 ID
        refresh_token: 要测试的 refresh_token
    """
    print("\n" + "=" * 60)
    print("测试 Refresh Token")
    print("=" * 60)

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority="https://login.microsoftonline.com/common"
    )

    result = app.acquire_token_by_refresh_token(
        refresh_token=refresh_token,
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" in result:
        print("✅ Refresh Token 有效！")
        print(f"Access Token: {result['access_token'][:50]}...")
        print(f"Expires In: {result.get('expires_in', 3600)} 秒")
        return True
    else:
        print("❌ Refresh Token 无效或已过期")
        print(f"错误: {result.get('error')}")
        print(f"错误描述: {result.get('error_description')}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Microsoft OAuth2 Refresh Token 获取工具")
    print("=" * 60)

    # 获取 client_id
    print("\n请输入你的 Azure AD 应用客户端 ID：")
    print("（如果没有，请先在 Azure Portal 创建应用注册）")
    client_id = input("Client ID: ").strip()

    if not client_id:
        print("❌ 错误：Client ID 不能为空")
        return

    # 选择方法
    print("\n请选择获取 Refresh Token 的方法：")
    print("1. 设备码流程（推荐，适合命令行环境）")
    print("2. 交互式登录（需要图形界面）")
    print("3. 测试现有的 Refresh Token")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    if choice == "1":
        refresh_token = get_refresh_token_device_flow(client_id)
        if refresh_token:
            print("\n是否要测试此 Refresh Token？(y/n): ", end="")
            if input().strip().lower() == "y":
                test_refresh_token(client_id, refresh_token)

    elif choice == "2":
        refresh_token = get_refresh_token_interactive(client_id)
        if refresh_token:
            print("\n是否要测试此 Refresh Token？(y/n): ", end="")
            if input().strip().lower() == "y":
                test_refresh_token(client_id, refresh_token)

    elif choice == "3":
        print("\n请输入要测试的 Refresh Token：")
        refresh_token = input("Refresh Token: ").strip()
        if refresh_token:
            test_refresh_token(client_id, refresh_token)
        else:
            print("❌ 错误：Refresh Token 不能为空")

    else:
        print("❌ 错误：无效的选项")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
