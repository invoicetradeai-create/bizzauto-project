# worker.py (Unified)
import threading
import time
import json
import os
from redis_client import redis_client
from ocr_tasks import process_invoice_image_gcp
from uuid import UUID
from datetime import datetime, timedelta

# Import scheduler logic from the existing scheduler_worker.py
from scheduler_worker import send_daily_stock_summary, process_pending_messages 

# --- JOB 1: THE SCHEDULER (Runs every 60 seconds) ---
def run_scheduler_loop():
    print("⏰ Scheduler Thread Started...")
    last_summary_sent_date = None
    
    while True:
        try:
            # 1. Daily Stock Summary
            current_date = datetime.now().date()
            if current_date != last_summary_sent_date:
                send_daily_stock_summary()
                last_summary_sent_date = current_date

            # 2. Process Pending WhatsApp Messages
            process_pending_messages()
            
        except Exception as e:
            print(f"Error in Scheduler Thread: {e}")
        
        # Sleep for 60 seconds
        print("⏰ Scheduler sleeping for 60s...")
        time.sleep(60)

# --- JOB 2: THE OCR WORKER (Waits for Redis jobs) ---
def run_ocr_redis_listener():
    print("📸 OCR Redis Listener Started...")
    
    # Use the imported redis_client instance directly
    redis_client_worker = redis_client

    while True:
        try:
            # This blocks until an item appears in 'ocr_queue'
            # timeout=10 means it will wait for 10 seconds then return None
            result = redis_client_worker.blpop("ocr_queue", timeout=10)
            
            if result:
                _, job_payload_json = result
                print(f"📥 Received OCR job: {job_payload_json}")
                
                try:
                    job_payload = json.loads(job_payload_json)
                    gcs_uri = job_payload.get("gcs_uri")
                    company_id_str = job_payload.get("company_id")
                    
                    if gcs_uri and company_id_str:
                        print(f"⚙️ Processing OCR for: {gcs_uri}")
                        process_invoice_image_gcp(gcs_uri, UUID(company_id_str))
                        print(f"✅ Finished OCR for: {gcs_uri}")
                        
                except Exception as e:
                    print(f"❌ Error processing OCR job: {e}")
            
        except Exception as e:
            print(f"⚠️ Redis Listener Error: {e}")
            time.sleep(5) # Wait before retrying connection

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print("🚀 Starting Unified Worker Service...")

        # 1. Create a Thread for the Scheduler
        scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
        scheduler_thread.start()

        # 2. Run the OCR listener in the Main Thread
        run_ocr_redis_listener()
    except Exception as e:
        import traceback
        print("💥 CRITICAL ERROR during Unified Worker startup or main loop:")
        print(f"Error: {e}")
        traceback.print_exc()