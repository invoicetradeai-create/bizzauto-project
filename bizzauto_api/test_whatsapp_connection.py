import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_whatsapp_connection(recipient_phone: str):
    """
    Performs a standalone test of the connection to the WhatsApp Cloud API.
    """
    print("--- Starting WhatsApp Connection Test ---")

    # 1. Get credentials from environment variables
    access_token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("PHONE_NUMBER_ID")
    api_version = "v19.0"

    if not access_token or not phone_number_id:
        print("\n❌ ERROR: Make sure WHATSAPP_TOKEN and PHONE_NUMBER_ID are set in your environment or .env file.")
        return

    print(f"✅ Credentials loaded (Token: ...{access_token[-4:]}, Phone ID: {phone_number_id})")

    # 2. Prepare the request
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": "This is a connection test from the diagnostic script."}
    }
    
    print(f"🌍 Sending POST request to: {url}")
    print(f"📄 Payload: {payload}")

    # 3. Make the API call with a timeout
    try:
        async with httpx.AsyncClient() as client:
            print("\n⏳ Sending request... (Timeout set to 15 seconds)")
            response = await client.post(url, headers=headers, json=payload, timeout=15.0)
            
            print(f"\n✅ Request completed with Status Code: {response.status_code}")
            print("📝 Response Body:")
            print(response.text)

            if response.is_success:
                print("\n--- ✅ SUCCESS: The connection to WhatsApp API is working. ---")
            else:
                print("\n--- ❌ FAILURE: The API call failed. Check the response body above for details. ---")

    except httpx.TimeoutException:
        print("\n--- ❌ CRITICAL FAILURE: The request timed out after 15 seconds. ---")
        print("This strongly suggests a network issue (firewall, DNS, proxy) is blocking the connection to graph.facebook.com.")
    except httpx.ConnectError as e:
        print(f"\n--- ❌ CRITICAL FAILURE: A connection error occurred: {e} ---")
        print("This could be a DNS issue or a problem with your machine's network configuration.")
    except Exception as e:
        print(f"\n--- ❌ An unexpected error occurred: {e} ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_whatsapp_connection.py <RECIPIENT_PHONE_NUMBER>")
        print("Example: python test_whatsapp_connection.py 923421234567")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    asyncio.run(test_whatsapp_connection(phone_number))
