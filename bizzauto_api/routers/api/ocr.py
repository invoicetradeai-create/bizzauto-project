import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from redis_config import queue
from ocr_tasks import process_invoice_image_gcp

router = APIRouter()

@router.post("/upload")
async def upload_invoice_for_ocr(file: UploadFile = File(...)):
    """
    Accepts an image file upload, saves it temporarily, and enqueues it for OCR processing.
    """
    try:
        # Ensure the temp directory exists
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "temp_media")
        os.makedirs(temp_dir, exist_ok=True)

        # Get the file extension
        extension = os.path.splitext(file.filename)[1]

        # Save the uploaded file to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=extension, dir=temp_dir)
        
        with os.fdopen(fd, 'wb') as temp_file:
            content = await file.read()
            temp_file.write(content)

        print(f"File '{file.filename}' uploaded and saved to: {temp_path}")

        # Enqueue the OCR processing task
        queue.enqueue(process_invoice_image_gcp, temp_path)
        print(f"Enqueued OCR task for image: {temp_path}")

        return {
            "message": "File uploaded successfully and queued for OCR processing.",
            "filename": file.filename,
            "temp_path": temp_path
        }
    except Exception as e:
        print(f"Error during file upload or queuing: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
