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

    # Check if the text matches the inventory format (ITEM CODE, ITEM NAME, BALANCE QUANTITY)
    if is_inventory_format(text):
        logger.info("Detected inventory format - parsing as inventory list")
        parsed_data["line_items"] = parse_inventory_format(text)
        parsed_data["total_amount"] = calculate_inventory_total(parsed_data["line_items"])
        return parsed_data

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


def is_inventory_format(text: str) -> bool:
    """
    Checks if the text matches the inventory format with ITEM CODE, ITEM NAME, and BALANCE QUANTITY.
    """
    # Look for the header pattern or typical structure of the inventory format
    text_upper = text.upper()

    # Check if text contains all the key terms that indicate inventory format
    has_item_code = 'ITEM CODE' in text_upper
    has_item_name = 'ITEM NAME' in text_upper
    has_balance_quantity = 'BALANCE' in text_upper and 'QUANTITY' in text_upper

    # Additional check for "VALUATION REPORT" which appears in the example
    has_valuation_report = 'VALUATION REPORT' in text_upper

    # If we have the key headers or the valuation report indicator, it's likely inventory format
    if (has_item_code and has_item_name and (has_balance_quantity or has_valuation_report)):
        return True

    # Look for the specific pattern in the text (could be comma-separated or in different lines)
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if 'ITEM CODE' in line.upper() and 'ITEM NAME' in line.upper():
            return True
        # Check for lines that look like the example format: code, name, quantity
        parts = line.split(',')
        if len(parts) >= 3:
            # Check if first part looks like an item code (alphanumeric), second is text, third is a number
            code_part = parts[0].strip()
            name_part = parts[1].strip()
            qty_part = parts[2].strip()

            # If the first part looks like a code (alphanumeric), second like a name, and third like a number
            if code_part.replace(' ', '').isalnum() and name_part and qty_part.isdigit():
                return True

    return False


def parse_inventory_format(text: str) -> List[Dict[str, Any]]:
    """
    Parses the inventory format with ITEM CODE, ITEM NAME, and BALANCE QUANTITY.
    Handles both comma-separated format and multi-line format from OCR.
    """
    logger.info("Parsing inventory format...")
    items = []

    lines = text.split('\n')

    # First, let's identify where the actual data starts by finding the headers
    header_indices = {}
    data_start_line = 0

    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        if 'ITEM CODE' in line_upper:
            header_indices['code'] = i
        elif 'ITEM NAME' in line_upper:
            header_indices['name'] = i
        elif 'BALANCE' in line_upper and 'QUANTITY' in line_upper:
            header_indices['quantity'] = i
        elif 'BALANCE' in line_upper and 'QUANTI' in line_upper:  # Handle potential OCR misrecognition
            header_indices['quantity'] = i

    # If we have headers on separate lines, try to parse the following lines
    if header_indices:
        # Find the first line after all headers - this is where data starts
        data_start_line = max(header_indices.values()) + 1

        # Look for lines that contain the pattern of item code, name, and quantity
        # Since OCR might have separated the columns across multiple lines or in different formats,
        # we need to be flexible in our parsing
        for i in range(data_start_line, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Check if this line contains comma-separated values
            parts = line.split(',')
            if len(parts) >= 3:
                item_code = parts[0].strip()
                item_name = parts[1].strip()
                quantity_str = parts[2].strip()

                # Skip if it's the total line
                if ('Total' in item_name and item_code == '') or ('Total' in item_code):
                    continue

                # Validate that quantity is a number
                try:
                    quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else 0

                    # Only add if we have a valid code and quantity
                    if item_code and quantity >= 0:
                        item_data = {
                            "name": item_name if item_name else f"Item {item_code}",
                            "quantity": quantity,
                            "price": 0.0,  # Price is not provided in inventory format, so set to 0
                            "total": 0.0   # Total is calculated as price * quantity, so also 0
                        }

                        items.append(item_data)
                        logger.debug(f"Inventory item parsed: {item_data}")

                except ValueError:
                    # If quantity is not a number, skip this line
                    continue
            else:
                # Try to parse as multi-column format where each column might be in the same line
                # Pattern: Some alphanumeric code, followed by text, followed by a number
                # Example: "00000191 17 PM 512 1" or similar
                words = line.split()
                if len(words) >= 3:
                    # Look for patterns like: [code] [name...] [quantity]
                    # The code is likely alphanumeric, the last element is likely a number (quantity)
                    possible_code = words[0]
                    possible_quantity_str = words[-1] if words[-1].isdigit() else None

                    if possible_code.isalnum() and possible_quantity_str:
                        item_code = possible_code
                        quantity = int(possible_quantity_str)
                        # The name would be the middle elements
                        item_name_parts = words[1:-1]  # Exclude first (code) and last (quantity)
                        item_name = ' '.join(item_name_parts) if item_name_parts else f"Item {item_code}"

                        # Skip if it's the total line
                        if 'Total' in item_name or 'TOTAL' in item_name.upper():
                            continue

                        item_data = {
                            "name": item_name,
                            "quantity": quantity,
                            "price": 0.0,
                            "total": 0.0
                        }

                        items.append(item_data)
                        logger.debug(f"Inventory item parsed from multi-column: {item_data}")

    logger.info(f"Parsed {len(items)} inventory items")
    return items


def calculate_inventory_total(items: List[Dict[str, Any]]) -> float:
    """
    Calculates the total amount for inventory items (typically the sum of quantities since prices are not provided).
    """
    # Since inventory format doesn't include prices, we'll return the total quantity
    # Or we could return 0 since prices are not available
    return sum(item['quantity'] for item in items)
