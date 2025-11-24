import os
import json
from google.cloud import storage
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ocr_tasks import process_invoice_image_gcp
from uuid import UUID, uuid4
from ...redis_client import get_redis_client # Adjust import path

# This is a placeholder for your actual authentication dependency
# You would replace this with your actual dependency to get the current user
async def get_current_user():
    # In a real application, this would return the authenticated user object
    # For now, we'll return a dummy user with a hardcoded company_id
    class DummyUser:
        company_id: UUID = UUID("94bb2f7b-5ce9-4f9b-b097-5ef45e75c2fa") # Replace with a valid company_id from your db
    return DummyUser()

router = APIRouter()

@router.post("/upload")
async def upload_invoice_for_ocr(file: UploadFile = File(...), current_user = Depends(get_current_user), r = Depends(get_redis_client)):
    """
    Accepts an image file upload, uploads it to GCS, and enqueues it for OCR processing.
    """
    try:
        gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not gcs_bucket_name:
            raise HTTPException(status_code=500, detail="GCS_BUCKET_NAME environment variable not set.")

        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket_name)

        # Create a unique filename
        extension = os.path.splitext(file.filename)[1]
        file_name = f"{uuid4()}{extension}"
        
        blob = bucket.blob(file_name)
        
        # Upload the file
        blob.upload_from_file(file.file, content_type=file.content_type)
        
        gcs_uri = f"gs://{gcs_bucket_name}/{file_name}"
        print(f"File '{file.filename}' uploaded to: {gcs_uri}")

        # Enqueue the OCR processing task with the GCS URI to Redis list
        payload = {
            "gcs_uri": gcs_uri,
            "company_id": str(current_user.company_id)
        }
        r.rpush("ocr_queue", json.dumps(payload))
        print(f"Enqueued OCR task for image: {gcs_uri}")

        return {
            "message": "File uploaded successfully and queued for OCR processing.",
            "filename": file.filename,
            "gcs_uri": gcs_uri
        }
    except Exception as e:
        print(f"Error during file upload or queuing: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
