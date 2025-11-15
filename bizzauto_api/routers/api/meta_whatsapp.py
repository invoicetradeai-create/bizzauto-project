
import requests
import os
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from crud import create_whatsapp_log, get_companies, get_whatsapp_logs, update_whatsapp_log
from models import WhatsappLog as PydanticWhatsappLog

router = APIRouter()

# --- Environment Variables ---
ACCESS_TOKEN = os.environ.get("META_WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("META_WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("META_WHATSAPP_VERIFY_TOKEN")
API_VERSION = "v19.0"

# --- Pydantic Models for Request Bodies ---
class MessageRequest(BaseModel):
    to: str
    body: str

# --- API Endpoints ---

@router.post("/send-meta-whatsapp", tags=["Meta WhatsApp"])
def send_whatsapp_message(message_request: MessageRequest, db: Session = Depends(get_db)):
    """
    Sends a text message to a WhatsApp number using Meta's Graph API.
    """
    if not all([ACCESS_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN]):
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: Meta WhatsApp environment variables are not set."
        )

    url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": message_request.to,
        "type": "text",
        "text": {"body": message_request.body},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Log the outgoing message
        companies = get_companies(db, skip=0, limit=1)
        if companies:
            whatsapp_log = PydanticWhatsappLog(
                company_id=companies[0].id,
                message_type="outgoing",
                phone=message_request.to,
                message=message_request.body,
                status="sent"
            )
            create_whatsapp_log(db, whatsapp_log)
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Meta API: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to Meta API.")

@router.get("/webhook", tags=["Meta WhatsApp"])
def verify_webhook(request: Request):
    """
    Verifies the webhook subscription with Meta.
    """
    if not VERIFY_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: META_WHATSAPP_VERIFY_TOKEN is not set."
        )

    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return int(challenge)
    else:
        print("Webhook verification failed.")
        raise HTTPException(status_code=403, detail="Webhook verification failed.")

@router.post("/webhook", tags=["Meta WhatsApp"])
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives incoming messages and status updates from WhatsApp.
    """
    data = await request.json()
    print("Received webhook data:")
    print(data)

    companies = get_companies(db, skip=0, limit=1)
    if not companies:
        print("No companies found in the database.")
        return {"status": "success"}

    company_id = companies[0].id

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "messages" in value:
                for message in value.get("messages", []):
                    whatsapp_log = PydanticWhatsappLog(
                        company_id=company_id,
                        message_type="incoming",
                        phone=message.get("from"),
                        message=message.get("text", {}).get("body"),
                        status="received"
                    )
                    create_whatsapp_log(db, whatsapp_log)
            elif "statuses" in value:
                for status in value.get("statuses", []):
                    # Find the message by recipient phone and update its status
                    logs = get_whatsapp_logs(db, skip=0, limit=100) # A more efficient query would be needed in a real app
                    for log in logs:
                        if log.phone == status.get("recipient_id"):
                            log.status = status.get("status")
                            update_whatsapp_log(db, log.id, log)
                            break

    return {"status": "success"}
