"""
Test script: Test IMAP method for email retrieval
"""
import asyncio
import sys
import email
from email.header import decode_header
sys.path.insert(0, 'D:/DevSpace/H01_hotmail_reg/imap/backend')

import aioimaplib


async def test_imap():
    """Test IMAP method"""
    print("=" * 60)
    print("Testing IMAP Method")
    print("=" * 60)

    email_addr = "vsqamnadrz@hotmail.com"
    password = "xmcxihrzoszn80"

    print(f"\nEmail: {email_addr}")
    print(f"Password: {password}")

    try:
        print("\nStep 1: Connecting to IMAP server...")
        imap_client = aioimaplib.IMAP4_SSL(host="outlook.office365.com", port=993)
        await imap_client.wait_hello_from_server()
        print("Success: Connected to server")

        print("\nStep 2: Logging in...")
        response = await imap_client.login(email_addr, password)
        print(f"Login response: {response}")

        if response.result == "OK":
            print("Success: Logged in")

            print("\nStep 3: Selecting INBOX...")
            await imap_client.select("INBOX")
            print("Success: Selected INBOX")

            print("\nStep 4: Searching for latest emails...")
            _, msg_ids = await imap_client.search("ALL")
            msg_id_list = msg_ids[0].split()

            if msg_id_list:
                latest_ids = msg_id_list[-2:]  # Get last 2 emails
                print(f"Success: Found {len(msg_id_list)} total emails, fetching latest {len(latest_ids)}")

                for i, msg_id in enumerate(latest_ids, 1):
                    print(f"\n--- Email {i} (ID: {msg_id.decode()}) ---")
                    _, msg_data = await imap_client.fetch(msg_id, "(RFC822)")

                    # Parse email
                    raw_email = msg_data[1]
                    email_message = email.message_from_bytes(raw_email)

                    # Extract headers
                    subject = email_message.get("Subject", "")
                    from_addr = email_message.get("From", "")
                    to_addr = email_message.get("To", "")
                    date = email_message.get("Date", "")

                    print(f"Date: {date}")
                    print(f"From: {from_addr}")
                    print(f"To: {to_addr}")
                    print(f"Subject: {subject}")

                    # Extract body
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True)
                                if body:
                                    print(f"Body preview: {body[:200].decode('utf-8', errors='ignore')}...")
                                break
                    else:
                        body = email_message.get_payload(decode=True)
                        if body:
                            print(f"Body preview: {body[:200].decode('utf-8', errors='ignore')}...")

            else:
                print("Warning: INBOX is empty")

            await imap_client.logout()
            print("\nSuccess: IMAP method works!")
            return True
        else:
            print(f"Error: Login failed - {response}")
            return False

    except Exception as e:
        print(f"Error: IMAP test failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Email Retrieval Method Test")
    print("=" * 60)

    imap_success = await test_imap()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"IMAP: {'Success' if imap_success else 'Failed'}")

    if imap_success:
        print("\nRecommendation: Use IMAP method")
        print("Pros:")
        print("  - Standard protocol, good compatibility")
        print("  - Works with username/password")
        print("  - No need for Azure AD app")
        print("Cons:")
        print("  - Need to parse raw email format")
        print("  - Higher connection overhead")
        print("\nNote: The refresh_token provided appears to be expired.")
        print("For Graph API to work, you need a valid refresh_token from OAuth2 flow.")


if __name__ == "__main__":
    asyncio.run(main())
