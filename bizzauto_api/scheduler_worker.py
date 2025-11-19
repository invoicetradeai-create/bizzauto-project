import os
import time
import requests
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import crud
from database import SessionLocal
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage

# Load environment variables
load_dotenv()

# --- Environment Variables ---
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
API_VERSION = "v19.0"

def send_whatsapp_message(to: str, body: str) -> bool:
    """
    Sends a text message to a WhatsApp number using Meta's Graph API.
    Returns True if the message was sent successfully, False otherwise.
    """
    if not all([ACCESS_TOKEN, PHONE_NUMBER_ID]):
        print("Server configuration error: Meta WhatsApp environment variables are not set.")
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
        response_json = response.json() # Get the JSON response
        print(f"Successfully sent message to {to}")
        print(f"Meta API Response: {response_json}") # Print the response
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {to}: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        return False

def process_pending_messages():
    """
    Fetches and processes pending scheduled messages.
    """
    print("Checking for pending scheduled messages...")
    db: Session = SessionLocal()
    try:
        pending_messages = crud.get_pending_scheduled_whatsapp_messages(db)
        
        if not pending_messages:
            print("No pending messages to send.")
            return

        for message in pending_messages:
            print(f"Processing message ID: {message.id} to {message.phone}")
            
            success = send_whatsapp_message(to=message.phone, body=message.message)
            
            if success:
                message.status = 'sent'
            else:
                message.status = 'failed'
            
            # Update the message status in the database
            updated_message_pydantic = PydanticScheduledWhatsappMessage.model_validate(message)
            crud.update_scheduled_whatsapp_message(db, message.id, updated_message_pydantic)
            
            print(f"Updated status for message ID {message.id} to '{message.status}'")

    finally:
        db.close()

def main():
    """
    Main worker loop.
    """
    print("Starting scheduler worker...")
    while True:
        process_pending_messages()
        # Sleep for 60 seconds before checking again
        print("Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
