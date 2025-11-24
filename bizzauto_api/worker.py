# worker.py
import os
import json
import time
from redis_client import redis_client
from ocr_tasks import process_invoice_image_gcp
from uuid import UUID

def worker_process_ocr_jobs():
    """
    Continuously processes OCR jobs from the 'ocr_queue' in Redis.
    """
    print("OCR Worker started, waiting for jobs...")
    
    # Use the imported redis_client instance directly
    redis_client_worker = redis_client

    while True:
        try:
            # blpop is a blocking operation, it will wait for an item on the list
            # The '0' timeout means it will wait indefinitely
            _, job_payload_json = redis_client_worker.blpop("ocr_queue", timeout=0)
            
            if job_payload_json:
                print(f"Received job: {job_payload_json}")
                try:
                    job_payload = json.loads(job_payload_json)
                    gcs_uri = job_payload.get("gcs_uri")
                    company_id_str = job_payload.get("company_id")

                    if not gcs_uri or not company_id_str:
                        print(f"Skipping job due to missing 'gcs_uri' or 'company_id': {job_payload_json}")
                        continue

                    company_id = UUID(company_id_str)

                    print(f"Processing OCR job for GCS URI: {gcs_uri}, Company ID: {company_id}")
                    
                    # Perform the actual OCR processing
                    # This function should handle saving results to Supabase
                    process_invoice_image_gcp(gcs_uri, company_id)
                    
                    print(f"Successfully processed OCR job for GCS URI: {gcs_uri}")

                except json.JSONDecodeError:
                    print(f"Error decoding JSON payload: {job_payload_json}")
                    # Optionally, move to a "dead-letter" queue for inspection
                except (TypeError, ValueError) as e:
                    print(f"Invalid data in job payload: {job_payload_json}. Error: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing job {job_payload_json}. Error: {e}")
        
        except ConnectionError as e:
            print(f"Redis connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred in the worker loop: {e}. Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    worker_process_ocr_jobs()
