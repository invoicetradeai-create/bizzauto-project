# worker.py (Unified, Self-Contained)
import threading
import time
import json
import os
import requests
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# --- IMPORTS FROM YOUR PROJECT ---
from redis_client import redis_client
from ocr_tasks import process_invoice_image_gcp 
from database import SessionLocal
import crud
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage
from sql_models import Setting, Company

# --- PRINT AT TOP TO VERIFY LOAD ---
print("✅ Worker Module Loaded...", flush=True)

# Load environment variables for scheduler functions
load_dotenv()

# --- Environment Variables for WhatsApp ---
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
API_VERSION = "v19.0"

# --- HELPER FUNCTIONS (Scheduler Logic, moved from scheduler_worker.py) ---

def send_whatsapp_message(to: str, body: str) -> bool:
    """
    Sends a text message to a WhatsApp number using Meta's Graph API.
    """
    if not all([ACCESS_TOKEN, PHONE_NUMBER_ID]):
        print("Server configuration error: Meta WhatsApp environment variables are not set.", flush=True)
        return False

    url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully sent message to {to}", flush=True)
        print(f"Meta API Response: {response.json()}", flush=True)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {to}: {e}", flush=True)
        if e.response is not None:
            print(f"Response body: {e.response.text}", flush=True)
        return False

def process_pending_messages():
    """
    Fetches and processes pending scheduled messages.
    """
    print("Checking for pending scheduled messages...", flush=True)
    db: Session = SessionLocal()
    try:
        pending_messages = crud.get_pending_scheduled_whatsapp_messages(db)
        if not pending_messages:
            return

        for message in pending_messages:
            print(f"Processing message ID: {message.id} to {message.phone}", flush=True)
            success = send_whatsapp_message(to=message.phone, body=message.message)
            message.status = 'sent' if success else 'failed'
            updated_message_pydantic = PydanticScheduledWhatsappMessage.model_validate(message, from_attributes=True)
            crud.update_scheduled_whatsapp_message(db, message.id, updated_message_pydantic)
            print(f"Updated status for message ID {message.id} to '{message.status}'", flush=True)
    finally:
        db.close()

def send_daily_stock_summary():
    """
    Fetches low-stock and expiring products and sends alerts.
    """
    print("Running daily stock check...", flush=True)
    db: Session = SessionLocal()
    try:
        companies = crud.get_companies(db)
        if not companies:
            return

        for company in companies:
            admin_setting = db.query(Setting).filter(Setting.key == "admin_whatsapp_number").first() # Simplified for now
            admin_phone_number = None
            if admin_setting and admin_setting.value:
                try:
                    admin_phone_number = json.loads(admin_setting.value).get("phone")
                except json.JSONDecodeError:
                    admin_phone_number = admin_setting.value
            
            if not admin_phone_number:
                continue

            alert_products = crud.get_alert_products(db, company_id=company.id, days_to_expiry=30)
            if not alert_products:
                continue

            message_body = f"*Inventory Alerts for {company.name}:*\n\n"
            low_stock_items = [f"- {p.name} - Stock: {p.stock_quantity}" for p in alert_products if p.stock_quantity <= p.low_stock_alert]
            expiring_items = [f"- {p.name} - Expires: {p.expiration_date.strftime('%Y-%m-%d')}" for p in alert_products if p.expiration_date and p.expiration_date.date() <= (datetime.utcnow().date() + timedelta(days=30))]

            if low_stock_items:
                message_body += """*Low Stock Items:*\n""" + "\n".join(low_stock_items) + "\n\n"
            
            if expiring_items:
                message_body += """*Expiring Items (within 30 days):*\n""" + "\n".join(expiring_items) + "\n\n"

            if low_stock_items or expiring_items:
                send_whatsapp_message(to=admin_phone_number, body=message_body)
                print(f"Alert sent to {admin_phone_number} for company {company.name}.", flush=True)
    finally:
        db.close()

# --- JOB 1: THE SCHEDULER LOOP ---
def run_scheduler_loop():
    print("⏰ Scheduler Thread Started...", flush=True)
    last_summary_sent_date = None
    
    while True:
        try:
            current_date = datetime.now().date()
            if current_date != last_summary_sent_date:
                send_daily_stock_summary()
                last_summary_sent_date = current_date
            process_pending_messages()
        except Exception as e:
            print(f"Error in Scheduler Thread: {e}", flush=True)
        time.sleep(60)

# --- JOB 2: THE OCR REDIS LISTENER ---
def run_ocr_redis_listener():
    print("👀 OCR Redis Listener Started...", flush=True)
    
    try:
        redis_client_worker = redis_client
    except Exception as e:
        print(f"❌ Failed to connect to Redis in Worker: {e}", flush=True)
        return

    while True:
        try:
            result = redis_client_worker.blpop("ocr_queue", timeout=10)
            if result:
                _, job_payload_json = result
                print(f"📥 Received OCR job: {job_payload_json}", flush=True)
                try:
                    job_payload = json.loads(job_payload_json)
                    gcs_uri = job_payload.get("gcs_uri")
                    company_id_str = job_payload.get("company_id")
                    
                    if gcs_uri and company_id_str:
                        print(f"⚙️ Processing OCR for: {gcs_uri}", flush=True)
                        process_invoice_image_gcp(gcs_uri, UUID(company_id_str))
                        print(f"✅ Finished OCR for: {gcs_uri}", flush=True)
                except Exception as e:
                    print(f"❌ Error processing OCR job: {e}", flush=True)
        except Exception as e:
            print(f"⚠️ Redis Listener Error: {e}", flush=True)
            time.sleep(5)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # --- Google Cloud Credentials Setup (Mirrors main.py) ---
    try:
        creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not creds_json:
            raise ValueError("Env var GOOGLE_APPLICATION_CREDENTIALS_JSON is not set for worker")

        creds_dict = json.loads(creds_json)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        with open("/tmp/sa_worker.json", "w") as f:
            json.dump(creds_dict, f)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/sa_worker.json"
        print("✅ Google Cloud Vision API credentials configured for worker.", flush=True)
    except Exception as e:
        print(f"❌ Error configuring Google Cloud Vision API credentials for worker: {e}", flush=True)
    # --- End of Credentials Setup ---

    print("🚀 Starting Unified Worker Service...", flush=True)
    scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    scheduler_thread.start()
    run_ocr_redis_listener()
