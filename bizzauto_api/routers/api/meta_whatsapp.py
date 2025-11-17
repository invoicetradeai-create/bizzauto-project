
import requests
import os
import tempfile
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from crud import create_whatsapp_log, get_companies, get_whatsapp_logs, update_whatsapp_log
from models import WhatsappLog as PydanticWhatsappLog
from redis_config import queue
from ocr_tasks import process_invoice_image_gcp

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

def download_media_file(media_id: str, access_token: str) -> str | None:
    """
    Downloads a media file from Meta's servers and saves it temporarily.
    Returns the path to the saved file, or None if an error occurs.
    """
    try:
        # 1. Get media URL
        url = f"https://graph.facebook.com/{API_VERSION}/{media_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media_info = response.json()
        media_url = media_info.get("url")

        if not media_url:
            print("Error: Media URL not found in response.")
            return None

        # 2. Download the actual media file
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()

        # 3. Save to a temporary file
        content_type = media_response.headers.get("Content-Type", "application/octet-stream")
        extension = content_type.split("/")[-1] if "/" in content_type else "tmp"
        
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "temp_media")
        os.makedirs(temp_dir, exist_ok=True)

        # Use a temporary file to save the media
        fd, temp_path = tempfile.mkstemp(suffix=f".{extension}", dir=temp_dir)
        
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(media_response.content)
        
        print(f"Media file saved to: {temp_path}")
        return temp_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading media file: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during media download: {e}")
        return None


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
        # Meta expects the challenge as a plain integer, not in a JSON object
        return int(challenge)
    else:
        print("Webhook verification failed.")
        raise HTTPException(status_code=403, detail="Webhook verification failed.")

@router.post("/webhook", tags=["Meta WhatsApp"])
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives incoming messages and status updates from WhatsApp.
    If an image is received, it triggers the OCR processing task.
    """
    data = await request.json()
    print("Received webhook data:")
    print(data)

    # Acknowledge the webhook immediately to avoid retries from Meta
    # The actual processing will happen in the background
    
    companies = get_companies(db, skip=0, limit=1)
    if not companies:
        print("No companies found in the database. Cannot process webhook.")
        return {"status": "success"}

    company_id = companies[0].id

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "messages" in value:
                for message in value.get("messages", []):
                    message_type = message.get("type")
                    
                    # Handle incoming text messages
                    if message_type == "text":
                        whatsapp_log = PydanticWhatsappLog(
                            company_id=company_id,
                            message_type="incoming",
                            phone=message.get("from"),
                            message=message.get("text", {}).get("body"),
                            status="received"
                        )
                        create_whatsapp_log(db, whatsapp_log)
                    
                    # Handle incoming image messages
                    elif message_type == "image":
                        print("Image message received. Triggering OCR.")
                        media_id = message.get("image", {}).get("id")
                        if media_id and ACCESS_TOKEN:
                            image_path = download_media_file(media_id, ACCESS_TOKEN)
                            if image_path:
                                # Enqueue the OCR processing task
                                queue.enqueue(process_invoice_image_gcp, image_path)
                                print(f"Enqueued OCR task for image: {image_path}")
                                
                                # Log that we received an image
                                whatsapp_log = PydanticWhatsappLog(
                                    company_id=company_id,
                                    message_type="incoming_image",
                                    phone=message.get("from"),
                                    message=f"Image received, enqueued for OCR. Path: {image_path}",
                                    status="processing"
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
