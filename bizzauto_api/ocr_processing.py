import re
from typing import Dict, Any, List
import os # Added for environment variable access
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError # Added for specific API errors
from google.auth.exceptions import DefaultCredentialsError # Added for specific credential errors
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_file(file_content: bytes) -> str:
    """
    Extracts text from a file (PDF/image) using Google Cloud Vision API.
    Includes enhanced error logging for credential diagnosis.
    """
    client = None
    try:
        # Check if GOOGLE_APPLICATION_CREDENTIALS is set
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            logger.info(f"Using credentials from GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
        else:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Attempting to use default credentials.")

        client = vision.ImageAnnotatorClient()
        logger.info("Google Vision API client initialized successfully.")
    except DefaultCredentialsError as e:
        logger.error(f"❌ Google Vision API credential error: {e}. Please ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly or default credentials are available.")
        raise Exception(f"Google Vision API credential error: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error initializing Google Vision API client: {e}")
        raise Exception(f"Google Vision API client initialization failed: {e}")

    try:
        image = vision.Image(content=file_content)
        response = client.text_detection(image=image)

        if response.error.message:
            error_message = f"Google Vision API response error: {response.error.message}"
            logger.error(f"❌ {error_message}. Full error details: {response.error}")
            raise Exception(error_message)
        
        texts = response.text_annotations
        if texts:
            logger.info("✅ Text extracted successfully by Google Vision API.")
            return texts[0].description
        logger.warning("Google Vision API extracted no text annotations.")
        return ""
    except GoogleAPIError as e:
        logger.error(f"❌ Google Vision API call error: {e}. Check network connectivity, API quotas, and service account permissions.")
        raise Exception(f"Google Vision API call error: {e}")
    except Exception as e:
        logger.error(f"❌ Error during OCR text detection: {e}")
        raise


def parse_invoice_text(text: str) -> Dict[str, Any]:
    """
    Parses OCR text to extract invoice details.
    This is a simplified parser and might need to be adjusted for specific invoice formats.
    """
    logger.info(f"OCR extracted text (first 500 chars): {text[:500]}")
    parsed_data = {
        "invoice_date": None,
        "total_amount": 0.0,
        "line_items": []
    }

    # 1. Extract Invoice Date
    # Regex for various date formats (DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD, Month DD, YYYY)
    date_patterns = [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{4}[-]\d{1,2}[-]\d{1,2})",
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4})"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed_data["invoice_date"] = match.group(1)
            break

    # 2. Extract Total Amount
    # Look for lines containing "Total", "Amount Due", etc.
    total_patterns = [
        r"(?:Total|Amount\sDue|Balance|TOTAL)\s*[:\s]*\$?([\d,]+\.\d{2})",
        r"TOTAL\s+([\d,]+\.\d{2})",
    ]
    for pattern in total_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Take the last match as it's most likely the grand total
                total_str = matches[-1].replace(",", "")
                parsed_data["total_amount"] = float(total_str)
                break
            except (ValueError, IndexError):
                continue
    
    # 3. Extract Line Items
    logger.info(f"Attempting to parse line items...")
    # This regex tries to capture: [Description] [Optional Quantity] [Total Price]
    # It assumes the line item ends with a price.
    # The description can contain almost anything, but avoids "Total", "Subtotal", "Tax" at the start.
    line_item_pattern = re.compile(
        r"^(?!(?:Total|Subtotal|Tax|Shipping|Discount)\b)(.+?)(?:\s+(\d+))?\s+(\d+\.\d{2})$",
        re.MULTILINE | re.IGNORECASE
    )

    for match in line_item_pattern.finditer(text):
        item_full_desc = match.group(1).strip()
        quantity_str = match.group(2)
        total = float(match.group(3))

        quantity = int(quantity_str) if quantity_str else 1
        
        # Heuristic to separate item name from other potential numbers in description
        # This is still a simplification, better would be to look for distinct columns
        item_name = re.sub(r'\s*\d+(\.\d{2})?(\s*x\s*\d+)?$', '', item_full_desc).strip()

        # If item_name is empty after cleaning, use the full description
        if not item_name:
            item_name = item_full_desc

        # Avoid adding total line again as a line item
        if any(keyword in item_name for keyword in ["Total", "Subtotal", "Tax", "Shipping", "Discount"]):
            continue

        # Basic validation
        if quantity > 0 and total > 0 and item_name:
            item_data = {
                "name": item_name,
                "quantity": quantity,
                "price": round(total / quantity, 2), # Calculate unit price
                "total": total
            }
            logger.debug(f"Primary pattern matched item: {item_data}") # Added debug log
            parsed_data["line_items"].append(item_data)
    
    # If no line items were found with the complex regex, try a simpler one.
    # This refined simpler pattern looks for a line ending with a price and tries to extract quantity.
    if not parsed_data["line_items"]:
        logger.info("No line items found with primary pattern, trying refined simpler pattern.")
        
        # New simpler line item pattern: Looks for any text followed by a price,
        # then tries to infer quantity from the beginning of the text part.
        simple_line_item_pattern = re.compile(
            r"^(?!.*\b(?:Total|Subtotal|Tax|Shipping|Discount)\b)(.+?)\s+\$?([\d,]+\.\d{2})$",
            re.MULTILINE | re.IGNORECASE
        )
        for match in simple_line_item_pattern.finditer(text):
            full_line_text_before_price = match.group(1).strip() # Everything before the final price
            total_str = match.group(2).replace(",", "")
            total = float(total_str)

            item_name = full_line_text_before_price
            quantity = 1 # Default quantity

            # Try to extract quantity from the beginning of the full_line_text_before_price
            # e.g., "2 Item Name" -> quantity=2, item_name="Item Name"
            qty_match = re.match(r"(\d+)\s+(.*)", full_line_text_before_price)
            if qty_match:
                try:
                    quantity = int(qty_match.group(1))
                    item_name = qty_match.group(2).strip()
                except ValueError:
                    # If quantity extraction fails, keep default quantity and original item_name
                    quantity = 1
                    item_name = full_line_text_before_price

            # Avoid adding total/tax lines as line items after quantity extraction
            if any(keyword in item_name for keyword in ["Total", "Subtotal", "Tax", "Shipping", "Discount"]):
                logger.debug(f"Skipping potential line item (keyword in name after qty extraction): '{item_name}'")
                continue

            # Basic validation
            if quantity > 0 and total > 0 and item_name:
                item_data = {
                    "name": item_name,
                    "quantity": quantity,
                    "price": round(total / quantity, 2) if quantity > 0 else total, # Calculate unit price
                    "total": total
                }
                logger.debug(f"Refined simpler pattern matched item: {item_data}") # Added debug log
                parsed_data["line_items"].append(item_data)

    logger.info(f"Line items found: {len(parsed_data['line_items'])}")
    
    # If total amount is still zero, calculate it from line items
    if parsed_data["total_amount"] == 0.0 and parsed_data["line_items"]:
        parsed_data["total_amount"] = sum(item['total'] for item in parsed_data["line_items"])

    return parsed_data
