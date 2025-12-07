import re
import logging
from typing import Dict, Any, List
from google.cloud import vision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _parse_invoice_text(text: str) -> Dict[str, Any]:
    """
    Parses OCR text to extract invoice details.
    This is a simplified parser and might need to be adjusted for specific invoice formats.
    
    Args:
        text: The raw text extracted from the invoice.

    Returns:
        A dictionary with parsed data. If parsing fails, the 'items' list will be empty.
    """
    parsed_data = {
        "invoice_date": None,
        "total_amount": 0.0,
        "items": []
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
    # Look for lines containing "Total", "Amount Due", etc. and a numeric value.
    total_patterns = [
        r"(?:Total|Amount\sDue|Balance|TOTAL)\s*[:\s]*\$?([\d,]+\.\d{2})",
        r"TOTAL\s+([\d,]+\.\d{2})",
    ]
    total_amount = 0.0
    for pattern in total_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Take the last match as it's most likely the grand total
                total_str = matches[-1].replace(",", "")
                total_amount = float(total_str)
                break
            except (ValueError, IndexError):
                continue
    parsed_data["total_amount"] = total_amount

    # 3. Extract Line Items
    # This regex looks for lines that seem to contain a quantity, a description, and a price.
    # e.g., "2 Product A 10.00" or "Product B 1 20.50"
    # It's intentionally flexible to capture various formats.
    line_item_pattern = re.compile(
        r"^(?P<quantity>\d+)?\s*(?P<name>[\w\s\-\/]+?)\s+(?P<price>\d+\.\d{2})$",
        re.MULTILINE | re.IGNORECASE
    )

    for match in line_item_pattern.finditer(text):
        try:
            name = match.group("name").strip()
            # Avoid matching total/subtotal lines as items
            if any(keyword in name.lower() for keyword in ["total", "subtotal", "tax", "shipping"]):
                continue

            quantity_str = match.group("quantity")
            quantity = int(quantity_str) if quantity_str else 1
            
            price = float(match.group("price"))

            if name and price > 0:
                parsed_data["items"].append({
                    "product_name": name,
                    "quantity": quantity,
                    "price": price,
                })
        except (ValueError, AttributeError):
            continue # Ignore lines that don't parse correctly

    # If total amount is still zero, calculate it from line items
    if parsed_data["total_amount"] == 0.0 and parsed_data["items"]:
        parsed_data["total_amount"] = sum(item['price'] * item['quantity'] for item in parsed_data["items"])
        
    return parsed_data


def process_invoice_image_gcp(image_data: bytes) -> Dict[str, Any]:
    """
    Processes an invoice image/PDF from bytes using Google Cloud Vision API, 
    extracts text, parses it, and returns structured data.

    Args:
        image_data: The invoice file content as bytes.

    Returns:
        A dictionary containing the parsed invoice data.

    Raises:
        Exception: If the Google Cloud Vision API call fails.
    """
    try:
        # Initialize the client. Assumes GOOGLE_APPLICATION_CREDENTIALS is set in the environment.
        client = vision.ImageAnnotatorClient()
        
        # Create an image object from the byte data
        image = vision.Image(content=image_data)

        # Perform text detection
        response = client.text_detection(image=image)
        
        # Handle API errors
        if response.error.message:
            logger.error(f"Google Vision API error: {response.error.message}")
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        if response.text_annotations:
            # The first annotation contains the full detected text
            full_text = response.text_annotations[0].description
            logger.info("Successfully extracted text from image.")
            
            # Parse the extracted text
            parsed_data = _parse_invoice_text(full_text)
            return parsed_data
        else:
            logger.warning("No text found in the image by Google Vision API.")
            # Return empty structure if no text is found
            return {"invoice_date": None, "total_amount": 0.0, "items": []}
            
    except Exception as e:
        logger.error(f"An error occurred during OCR processing: {e}")
        # Re-raise the exception to be handled by the caller
        raise
