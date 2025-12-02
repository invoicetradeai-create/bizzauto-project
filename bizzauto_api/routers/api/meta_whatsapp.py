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
from crud import create_whatsapp_log, get_companies, get_whatsapp_logs, update_whatsapp_log, get_whatsapp_log_by_whatsapp_message_id, create_scheduled_whatsapp_message
from models import WhatsappLog as PydanticWhatsappLog
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage
from sql_models import User
from ocr_tasks import process_invoice_image_gcp
from whatsapp_utils import send_reply
from whatsapp_agent import run_whatsapp_agent
from pydantic import BaseModel
from typing import Any
from datetime import datetime
from dependencies import get_current_user

router = APIRouter()

# --- Environment Variables ---
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
API_VERSION = "v19.0"

# -----------------------------
# Background processing
# -----------------------------
async def process_whatsapp_message(entry_data: dict):
    print("\n" + "=" * 60)
    print("🚀 BACKGROUND TASK STARTED")
    print("=" * 60)
    
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

                            # --- 1. Look up user context & Log INCOMING (Short DB Session) ---
                            user_id_for_log = None
                            company_id_for_log = None
                            
                            db = SessionLocal()
                            try:
                                from sql_models import Client
                                from whatsapp_utils import sanitize_phone_number
                                
                                sanitized_phone = sanitize_phone_number(sender_phone)
                                client = db.query(Client).filter(Client.phone == sanitized_phone).first()

                                if not client:
                                    print(f"⚠️  No client found for phone number: {sender_phone}. Ignoring message.")
                                    continue

                                user_id_for_log = client.user_id
                                company_id_for_log = client.company_id
                                
                                if not user_id_for_log or not company_id_for_log:
                                    print(f"⚠️  Client {client.id} is missing user_id or company_id. Ignoring message.")
                                    continue
                                    
                                print(f"✅ Found context: User ID {user_id_for_log}, Company ID {company_id_for_log}")

                                # Log INCOMING Message
                                try:
                                    incoming_log = PydanticWhatsappLog(
                                        company_id=company_id_for_log,
                                        user_id=user_id_for_log,
                                        message_type="text",
                                        whatsapp_message_id=message_id,
                                        phone=sender_phone,
                                        message=incoming_text,
                                        status="received"
                                    )
                                    create_whatsapp_log(db, incoming_log)
                                except Exception as e:
                                    print(f"❌ Failed to log incoming message: {e}")
                                    traceback.print_exc() # Add full traceback for detailed debugging
                            finally:
                                db.close()

                            if not user_id_for_log:
                                continue
                                
                            # --- 3. Run Agent (No DB Connection Held) ---
                            reply = await run_whatsapp_agent(incoming_text, sender_phone)
                            
                            if not reply:
                                continue

                            # --- 4. Send Reply (No DB Connection Held) ---
                            send_result = await send_reply(to=sender_phone, data=reply) # FIX APPLIED HERE

                            whatsapp_message_id_for_log = None
                            if send_result and "messages" in send_result and len(send_result["messages"]) > 0:
                                whatsapp_message_id_for_log = send_result["messages"][0].get("id")

                            # --- 5. Log OUTGOING Message (Short DB Session) ---
                            db = SessionLocal()
                            try:
                                new_log = PydanticWhatsappLog(
                                    company_id=company_id_for_log,
                                    user_id=user_id_for_log,
                                    message_type="text",
                                    whatsapp_message_id=whatsapp_message_id_for_log,
                                    phone=sender_phone,
                                    message=reply,
                                    status="sent"
                                )
                                create_whatsapp_log(db, new_log)
                            except Exception as e:
                                print(f"❌ Failed to log outgoing message: {e}")
                                traceback.print_exc() # Add full traceback for detailed debugging
                            finally:
                                db.close()

    except Exception as e:
        print(f"Error in process_whatsapp_message: {e}") # More specific error message
        traceback.print_exc()
    
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
# Send Message Endpoint
# -----------------------------
class SendMessageRequest(BaseModel):
    to: str
    message_data: Any

@router.post("/send-meta-whatsapp")
async def send_meta_whatsapp_message(
    request: SendMessageRequest, 
    response: Response, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # 1. Send Message via Meta API
        api_response = await send_reply(to=request.to, data=request.message_data)
        
        if api_response and "messages" in api_response:
            # 2. Save to Database (so it shows in the table)
            try:
                message_body = request.message_data.get("text", {}).get("body", "") if isinstance(request.message_data, dict) else str(request.message_data)
                
                new_message = PydanticScheduledWhatsappMessage(
                    company_id=user.company_id,
                    phone=request.to,
                    message=message_body,
                    scheduled_at=datetime.utcnow(),
                    status='sent'
                )
                create_scheduled_whatsapp_message(db, new_message, user.id)
                print(f"✅ Immediate message saved to DB for {request.to}")
            except Exception as db_e:
                print(f"⚠️ Failed to save immediate message to DB: {db_e}")
                traceback.print_exc() # Add full traceback
            return {"success": True}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            print(f"❌ Failed to send message via Meta API: {api_response}") # Log API response
            return {"error": "Failed to send message"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(f"❌ Error in send_meta_whatsapp_message: {e}") # Log actual error
        traceback.print_exc() # Add full traceback
        return {"error": str(e)}


# -----------------------------
# Webhook to receive messages
# -----------------------------
@router.post("/webhook")
async def receive_webhook(request: Request):
    print("🔔 POST /webhook received a request")
    try:
        data = await request.json()
        print(f"📦 Webhook Payload: {json.dumps(data, indent=2)}")
        asyncio.create_task(process_whatsapp_message(data))
        return {"status": "received"}
    except Exception as e:
        print(f"❌ Error in POST /webhook: {e}")
        traceback.print_exc() # Add full traceback
        return {"status": "error", "message": str(e)}
    
@router.get("/test")
async def test_endpoint():
    return {
        "status": "working",
        "token_set": bool(ACCESS_TOKEN),
        "phone_id_set": bool(PHONE_NUMBER_ID),
        "verify_token_set": bool(VERIFY_TOKEN)
    }