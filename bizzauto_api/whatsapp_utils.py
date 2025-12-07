import re
import httpx
import os
from typing import Optional, Dict, Any

# =================================
# 1. PHONE NUMBER SANITIZATION (CRITICAL)
# =================================
def sanitize_phone_number(phone: str) -> str:
    """
    Removes +, spaces, dashes, and parentheses.
    Example: "+92 342 0024683" -> "923420024683"
    """
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)

# =================================
# 2. SEND AUTO REPLY (WHATSAPP CLOUD API)
# =================================
async def send_reply(to: str, data: Any) -> Optional[Dict[str, Any]]:
    """
    Sends a message using the WhatsApp Cloud API.
    Can be a simple text message (if data is a string) or a complex one like a template (if data is a dict).
    """
    access_token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("PHONE_NUMBER_ID")
    api_version = "v19.0"

    if not access_token or not phone_number_id:
        print("Error: WhatsApp environment variables not set.")
        return None

    clean_to = sanitize_phone_number(to)

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_to,
    }

    if isinstance(data, str):
        payload["type"] = "text"
        payload["text"] = {"body": data}
    elif isinstance(data, dict):
        payload.update(data)
    else:
        print("Error: Invalid data type for send_reply. Must be str or dict.")
        return None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            response_json = response.json()
            print(f"[send_reply] Success to {clean_to}")
            print(f"[Meta Response]: {response_json}")
            return response_json
        except httpx.HTTPStatusError as e:
            print(f"[send_reply] FAILED: {e.response.status_code}")
            print(f"[Body]: {e.response.text}")
            return e.response.json()
        except Exception as e:
            print(f"[send_reply] Error: {e}")
            return None