# routers/api/meta_whatsapp.py
import os
import tempfile
import asyncio
import requests
import json
import traceback
from fastapi import APIRouter, HTTPException, Request, Depends, Response, status
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from crud import create_whatsapp_log, get_companies, get_whatsapp_logs, update_whatsapp_log, get_whatsapp_log_by_whatsapp_message_id
from models import WhatsappLog as PydanticWhatsappLog
from ocr_tasks import process_invoice_image_gcp
from whatsapp_utils import send_reply
from whatsapp_agent import run_whatsapp_agent
from pydantic import BaseModel
from typing import Any

router = APIRouter()

# --- Environment Variables ---
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
API_VERSION = "v24.0"

# -----------------------------
# Background processing
# -----------------------------
async def process_whatsapp_message(entry_data: dict):
    print("\n" + "=" * 60)
    print("🚀 BACKGROUND TASK STARTED")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Log the entire payload
        print(f"📋 Entry data keys: {entry_data.keys()}")
        
        for entry in entry_data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                if "messages" in value:
                    for message in value.get("messages", []):
                        message_type = message.get("type")
                        sender_phone = message.get("from")
                        message_id = message.get("id")
                        
                        if message_type == "text":
                            incoming_text = message.get("text", {}).get("body", "").strip()
                            
                            if not incoming_text:
                                continue

                            # --- 1. Log INCOMING Message ---
                            # Get or create company for logging
                            companies = get_companies(db)
                            company_id_for_log = companies[0].id if companies else None
                            
                            if not company_id_for_log:
                                # Create a default company if none exists
                                from crud import create_company
                                from models import Company as PydanticCompany
                                default_company = create_company(db, PydanticCompany(name="Default Company", email="admin@bizzauto.com"))
                                company_id_for_log = default_company.id

                            try:
                                incoming_log = PydanticWhatsappLog(
                                    company_id=company_id_for_log,
                                    message_type="text",
                                    whatsapp_message_id=message_id,
                                    phone=sender_phone,
                                    message=incoming_text,
                                    status="received"
                                )
                                create_whatsapp_log(db, incoming_log)
                            except Exception as e:
                                print(f"❌ Failed to log incoming message: {e}")
                                
                            # --- 2. Run Agent ---
                            reply = await run_whatsapp_agent(incoming_text, sender_phone)
                            
                            if not reply:
                                continue

                            # --- 3. Send Reply ---
                            send_result = await send_reply(to=sender_phone, message=reply)

                            whatsapp_message_id = None
                            if send_result and "messages" in send_result and len(send_result["messages"]) > 0:
                                whatsapp_message_id = send_result["messages"][0].get("id")

                            # --- 4. Log OUTGOING Message ---
                            if company_id_for_log:
                                new_log = PydanticWhatsappLog(
                                    company_id=company_id_for_log,
                                    message_type="text",
                                    whatsapp_message_id=whatsapp_message_id,
                                    phone=sender_phone,
                                    message=reply,
                                    status="sent"
                                )
                                create_whatsapp_log(db, new_log)

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    
    finally:
        db.close()
        print("✅ BACKGROUND TASK FINISHED")

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
    else:
        raise HTTPException(status_code=403, detail="Webhook verification failed.")

# -----------------------------

class SendMessageRequest(BaseModel):
    to: str
    message_data: Any

@router.post("/send-meta-whatsapp")
async def send_meta_whatsapp_message(request: SendMessageRequest, response: Response, db: Session = Depends(get_db)):
    try:
        api_response = await send_reply(to=request.to, data=request.message_data)
        if api_response and "messages" in api_response:
            return {"success": True}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "Failed to send message"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}


# -----------------------------
# Webhook to receive messages
# -----------------------------
@router.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    asyncio.create_task(process_whatsapp_message(data))
    return {"status": "received"}
    
@router.get("/test")
async def test_endpoint():
    return {
        "status": "working",
        "token_set": bool(ACCESS_TOKEN),
        "phone_id_set": bool(PHONE_NUMBER_ID),
        "verify_token_set": bool(VERIFY_TOKEN)
    }