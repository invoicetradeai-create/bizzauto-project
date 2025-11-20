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

import json
import traceback # Add this import
from pydantic import BaseModel

# ... [keep other imports] ...

# ... [keep router and environment variables] ...


# -----------------------------
# Background processing (FIXED)
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
            print(f"📍 Processing entry: {entry.get('id')}")
            
            for change in entry.get("changes", []):
                value = change.get("value", {})
                print(f"🔍 Change value keys: {value.keys()}")

                if "messages" in value:
                    print(f"📨 Found {len(value['messages'])} message(s)")
                    
                    for message in value.get("messages", []):
                        message_type = message.get("type")
                        sender_phone = message.get("from")
                        message_id = message.get("id")
                        
                        print(f"\n📱 Message Details:")
                        print(f"   - Type: {message_type}")
                        print(f"   - From: {sender_phone}")
                        print(f"   - ID: {message_id}")

                        if message_type == "text":
                            incoming_text = message.get("text", {}).get("body", "")
                            print(f"   - Text: {incoming_text}")
                            
                            # Run agent
                            print(f"🤖 Running agent...")
                            reply = await run_whatsapp_agent(incoming_text, sender_phone)
                            print(f"✉️  Agent reply: {reply}")
                            
                            if not reply:
                                print("❌ Agent returned empty response!")
                                continue

                            # Send reply
                            print(f"📤 Sending to: {sender_phone}")
                            result = await send_reply(to=sender_phone, message=reply)
                            print(f"📬 Send result: {result}")
                        
                        else:
                            print(f"⚠️  Unsupported message type: {message_type}")
                
                else:
                    print("ℹ️  No 'messages' in value - might be status update")

    except Exception as e:
        print("\n" + "❌" * 30)
        print("💥 CRITICAL ERROR IN BACKGROUND TASK")
        print("❌" * 30)
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("❌" * 30 + "\n")
    
    finally:
        db.close()
        print("=" * 60)
        print("✅ BACKGROUND TASK FINISHED")
        print("=" * 60 + "\n")

# -----------------------------
# Webhook verification
# -----------------------------
@router.get("/webhook")
def verify_webhook(request: Request):
    """
    Handles webhook verification requests from Meta.
    Logs the incoming request and the verification result.
    """
    print("\n" + "="*50)
    print("🔎 WEBHOOK VERIFICATION RECEIVED")
    print("="*50)
    
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    print(f"🔹 Received params: {params}")
    print(f"🔹 Expected VERIFY_TOKEN: {VERIFY_TOKEN}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Verification successful. Returning challenge.")
        return int(challenge)
    else:
        print("❌ Verification failed.")
        print(f"   - Mode correct: {mode == 'subscribe'}")
        print(f"   - Token correct: {token == VERIFY_TOKEN}")
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
    print("=" * 50)
    print("🔔 WEBHOOK RECEIVED!")
    print("=" * 50)
    
    data = await request.json()
    print(f"📦 Raw data: {json.dumps(data, indent=2)}")
    
    asyncio.create_task(process_whatsapp_message(data))
    
    print("✅ Background task created")
    return {"status": "received"}
    
@router.get("/test")
async def test_endpoint():
    return {
        "status": "working",
        "token_set": bool(ACCESS_TOKEN),
        "phone_id_set": bool(PHONE_NUMBER_ID),
        "verify_token_set": bool(VERIFY_TOKEN)
    }