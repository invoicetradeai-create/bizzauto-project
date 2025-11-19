# routers/api/meta_whatsapp.py
import os
import tempfile
import asyncio
import requests
from fastapi import APIRouter, HTTPException, Request
# REMOVE Depends and Session from here if not used elsewhere in the route
from sqlalchemy.orm import Session

# 1. Import SessionLocal (the factory) instead of get_db
from database import SessionLocal 
from crud import create_whatsapp_log, get_companies, get_whatsapp_logs, update_whatsapp_log
from models import WhatsappLog as PydanticWhatsappLog
from redis_config import queue
from ocr_tasks import process_invoice_image_gcp
# Duplicate import removed
# Removed 'normalize_text' because it no longer exists in utils
from whatsapp_utils import send_reply
from whatsapp_agent import run_whatsapp_agent

router = APIRouter()

# --- Environment Variables ---
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
API_VERSION = "v24.0"

import traceback # Add this import
from pydantic import BaseModel

# ... [keep other imports] ...

# ... [keep router and environment variables] ...


# -----------------------------
# Background processing (FIXED)
# -----------------------------
async def process_whatsapp_message(entry_data: dict):
    print("--- [DEBUG] Background Task Started ---") # Debug marker
    db = SessionLocal()
    try:
        for entry in entry_data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                if "messages" in value:
                    for message in value.get("messages", []):
                        message_type = message.get("type")
                        sender_phone = message.get("from")

                        if message_type == "text":
                            incoming_text = message.get("text", {}).get("body", "")
                            
                            print(f"--- [DEBUG] Text received: {incoming_text}")
        
                            # 1. Check if Agent works
                            reply = await run_whatsapp_agent(incoming_text, sender_phone)
                            print(f"--- [DEBUG] Agent output: {reply}") 
                            
                            if not reply:
                                print("--- [ERROR] Agent returned empty response!")
                                return

                            # 2. Check the number being sent to
                            print(f"--- [DEBUG] Sending reply to raw number: {sender_phone}")
                            
                            await send_reply(to=sender_phone, message=reply)

    except Exception as e:
        # THIS IS THE MISSING PIECE
        print(f"--- [CRITICAL FAILURE] ---")
        traceback.print_exc() # This prints the exact line number of the error
    finally:
        db.close()
        print("--- [DEBUG] Background Task Finished ---")

# -----------------------------
# Webhook verification
# -----------------------------
@router.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed.")

# -----------------------------

class SendMessageRequest(BaseModel):
    to: str
    body: str

@router.post("/send-meta-whatsapp")
async def send_meta_whatsapp_message(request: SendMessageRequest):
    try:
        response = await send_reply(to=request.to, message=request.body)
        if response and "messages" in response:
            return {"status": "success", "data": response}
        else:
            # Try to get a more specific error from Meta's response
            error_message = "Failed to send message"
            if response and "error" in response and "message" in response["error"]:
                error_message = response["error"]["message"]
            raise HTTPException(status_code=500, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Webhook to receive messages
# -----------------------------
@router.post("/webhook")
async def receive_webhook(request: Request):
    # 4. Removed 'db: Session = Depends(get_db)' from arguments
    data = await request.json()
    
    # 5. Pass ONLY data, do not pass the 'db' object
    asyncio.create_task(process_whatsapp_message(data))
    
    return {"status": "received"}