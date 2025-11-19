import re
import string
import httpx
import os
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sql_models import Product

# =================================
# 1. INCOMING TEXT NORMALIZATION
# =================================
def normalize_text(msg: str) -> str:
    """
    Cleans and normalizes input text by converting to lowercase, trimming spaces,
    and removing emojis, specified punctuation, and extra whitespace.
    """
    # Convert to lowercase and trim leading/trailing spaces
    text = msg.lower().strip()

    # Remove emojis using a regex pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub(r'', text)

    # Remove specified punctuation
    punctuation_to_remove = '.,!?/'
    text = text.translate(str.maketrans('', '', punctuation_to_remove))

    # Collapse multiple spaces into a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =================================
# 2. PRODUCT AVAILABILITY CHECK
# =================================
def check_product_availability(db: Session, text: str) -> Optional[Dict[str, Any]]:
    """
    Checks for product names in a normalized text against the 'products' table in the PostgreSQL database.
    Returns the product dictionary if a match is found, otherwise None.
    """
    try:
        # Fetch all products from the PostgreSQL database
        print("--- Checking Product Availability ---")
        products = db.query(Product).all()
        
        if not products:
            print("DEBUG: No products found in the database.")
            return None
        
        normalized_text = text.lower()
        
        # --- Start Debug Logging ---
        print(f"DEBUG: Normalized incoming text: '{normalized_text}'")
        db_product_names = [p.name.lower().strip() for p in products]
        print(f"DEBUG: Product names from DB: {db_product_names}")
        # --- End Debug Logging ---

        text_words = set(normalized_text.split())

        # Iterate through products to find a match in the message
        for product in products:
            product_name = product.name
            if not product_name:
                continue

            normalized_product_name = product_name.lower().strip()
            
            # Check for full or partial phrase match
            if normalized_product_name in normalized_text:
                print(f"DEBUG: Found match (phrase in text): '{normalized_product_name}' in '{normalized_text}'")
                return {"name": product.name, "price": product.price, "stock_quantity": product.stock_quantity}

            # Check for word-by-word similarity
            product_words = set(normalized_product_name.split())
            if text_words.intersection(product_words):
                print(f"DEBUG: Found match (word intersection): {text_words.intersection(product_words)}")
                return {"name": product.name, "price": product.price, "stock_quantity": product.stock_quantity}

        print("DEBUG: No match found after checking all products.")
        return None
    except Exception as e:
        print(f"An error occurred while checking product availability: {e}")
        return None

# =================================
# 3. SEND AUTO REPLY (WHATSAPP CLOUD API)
# =================================
async def send_reply(to: str, message: str) -> Optional[Dict[str, Any]]:
    """
    Sends a simple text message using the WhatsApp Cloud API.
    """
    access_token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("PHONE_NUMBER_ID")
    api_version = "v20.0"

    if not access_token or not phone_number_id:
        print("Error: WhatsApp environment variables (WHATSAPP_TOKEN, PHONE_NUMBER_ID) are not set.")
        return None

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Successfully sent reply to {to}")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error sending WhatsApp message: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            return e.response.json()
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None

