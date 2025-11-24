import os
import time
import requests
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import crud
from database import SessionLocal
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage
from sql_models import Company, Setting
import json
from datetime import datetime, timedelta, time as dt_time

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

from datetime import datetime, time as dt_time

# ... (keep existing imports and functions)

def send_daily_stock_summary():
    """
    Fetches low-stock and expiring products for each company and sends alerts via WhatsApp.
    """
    print("Sending daily stock and expiry alerts...")
    db: Session = SessionLocal()
    try:
        companies = crud.get_companies(db)
        if not companies:
            print("No companies found to send alerts for.")
            return

        for company in companies:
            print(f"Processing alerts for company: {company.name} (ID: {company.id})")

            # Retrieve admin WhatsApp number from settings
            # Assuming a setting with key "admin_whatsapp_number" stores the contact
            admin_setting = db.query(Setting).filter(
                Setting.key == "admin_whatsapp_number"
            ).first() # TODO: Need to filter by user or company, currently fetching any matching setting
            
            admin_phone_number = None
            if admin_setting and admin_setting.value:
                try:
                    # Assuming value is stored as JSON string like {"phone": "+1234567890"}
                    setting_value = json.loads(admin_setting.value)
                    admin_phone_number = setting_value.get("phone")
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON for admin_whatsapp_number setting for company {company.id}")
                    admin_phone_number = admin_setting.value # Fallback to raw value if not JSON
            
            if not admin_phone_number:
                print(f"Skipping alerts for company {company.name}: Admin WhatsApp number not configured.")
                continue

            alert_products = crud.get_alert_products(db, company_id=company.id, days_to_expiry=30)

            if not alert_products:
                print(f"No low stock or expiring products for company {company.name}.")
                continue

            message_body = f"*Inventory Alerts for {company.name}:*\n\n"
            low_stock_items = []
            expiring_items = []

            current_date = datetime.utcnow().date() # Compare dates only

            for product in alert_products:
                if product.stock_quantity <= product.low_stock_alert:
                    low_stock_items.append(f"- {product.name} (SKU: {product.sku or 'N/A'}) - Stock: {product.stock_quantity}, Alert at: {product.low_stock_alert}")
                
                if product.expiration_date and product.expiration_date.date() <= (current_date + timedelta(days=30)):
                    expiring_items.append(f"- {product.name} (SKU: {product.sku or 'N/A'}) - Expires: {product.expiration_date.strftime('%Y-%m-%d')}")
            
            if low_stock_items:
                message_body += "*Low Stock Items:*\n" + "\n".join(low_stock_items) + "\n\n"
            
            if expiring_items:
                message_body += "*Expiring Items (within 30 days):*\n" + "\n".join(expiring_items) + "\n\n"

            if low_stock_items or expiring_items:
                send_whatsapp_message(to=admin_phone_number, body=message_body)
                print(f"Alert sent to {admin_phone_number} for company {company.name}.")
            else:
                print(f"No alerts generated despite products being returned for company {company.name}.")

    finally:
        db.close()


def main():
    """
    Main worker loop.
    """
    print("Starting scheduler worker...")
    last_summary_sent_date = None
    
    while True:
        # --- Daily Stock Summary ---
        # Check if it's time to send the daily summary (e.g., once per day)
        current_date = datetime.now().date()
        if current_date != last_summary_sent_date:
            send_daily_stock_summary()
            last_summary_sent_date = current_date

        # --- Process Pending Messages ---
        process_pending_messages()
        
        # Sleep for 60 seconds before checking again
        print("Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
