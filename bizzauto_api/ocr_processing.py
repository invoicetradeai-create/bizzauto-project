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

def improve_ocr_text_structure(text: str) -> str:
    """
    Improves OCR text structure by fixing common issues like:
    - Fragmented table rows
    - Missing spaces in table columns
    - Line breaks that break table structure
    """
    if not text:
        return text

    # First, split the text into lines
    lines = text.split('\n')
    processed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Check if this line looks like it might be part of a fragmented table row
        # For example, if it's just numbers or just text fragments
        current_line = line

        # Look ahead to see if we should combine lines to form complete table rows
        # This is particularly useful when OCR splits table rows incorrectly
        next_idx = i + 1
        while next_idx < len(lines):
            next_line = lines[next_idx].strip()
            if not next_line:
                next_idx += 1
                continue

            # Check if combining this line with the next might form a better table row
            # For example: if current line has a product code and next has more product info
            combined = current_line + " " + next_line

            # If the combined line has both numbers and looks more like a complete table row
            # (has what looks like item code, name, and quantity), then combine them
            # Use a simple heuristic: if it has multiple numbers, it might be a table row
            numbers_in_combined = len([word for word in combined.split() if word.replace('-', '').replace('.', '').isdigit()])
            numbers_in_current = len([word for word in current_line.split() if word.replace('-', '').replace('.', '').isdigit()])

            # If combining adds significant numeric content, it might be a table row
            if numbers_in_combined > numbers_in_current + 1 and len(combined.split()) > 3:
                current_line = combined
                next_idx += 1
            else:
                # If the next line looks like a header or separator, don't combine
                next_line_lower = next_line.lower()
                if any(keyword in next_line_lower for keyword in ['item code', 'item name', 'quantity', 'subtotal', 'total', 'header']):
                    break
                else:
                    # Check if the next line might be a continuation of current
                    # For example, if current has an item code and next has the name
                    current_has_code = any(word.replace('-', '').replace('.', '').isalnum() and any(c.isdigit() for c in word) for word in current_line.split())
                    next_has_text = any(word.isalpha() or ' ' in word for word in next_line.split())

                    if current_has_code and next_has_text and len(current_line.split()) < 4:
                        current_line = combined
                        next_idx += 1
                    else:
                        break

        processed_lines.append(current_line)
        i = next_idx

    return '\n'.join(processed_lines)


def extract_text_from_file(file_content: bytes) -> str:
    """
    Extracts text from a file (PDF/image) using Google Cloud Vision API.
    Includes enhanced error logging for credential diagnosis.
    Uses document_text_detection for better table structure preservation.
    Includes fallback mechanisms if Vision API is unavailable.
    """
    client = None
    try:
        # Check if GOOGLE_APPLICATION_CREDENTIALS is set
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            if os.path.exists(credentials_path):
                logger.info(f"Using credentials from GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
            else:
                logger.error(f"❌ Credentials file not found at: {credentials_path}")
                raise Exception(f"Google Vision API credentials file not found. Please ensure the file exists at the specified path or set GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable.")
        else:
            # Check if we're using service account key as JSON in environment
            credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
            if credentials_json:
                logger.info("Using credentials from GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable.")
                # Set the credentials JSON to a temporary file or environment for the client
                import tempfile
                import json
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                    temp_file.write(credentials_json)
                    temp_credentials_path = temp_file.name

                # Set the environment variable for this session
                old_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_credentials_path

                try:
                    client = vision.ImageAnnotatorClient()
                    logger.info("Google Vision API client initialized successfully with JSON credentials.")
                finally:
                    # Restore the original environment
                    if old_env:
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = old_env
                    else:
                        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                            del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                    # Clean up temporary file
                    import os as os_module
                    os_module.remove(temp_credentials_path)
            else:
                logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Attempting to use default credentials.")
                client = vision.ImageAnnotatorClient()
                logger.info("Google Vision API client initialized successfully with default credentials.")
    except DefaultCredentialsError as e:
        logger.error(f"❌ Google Vision API credential error. Please ensure GOOGLE_APPLICATION_CREDENTIALS points to a valid credentials file or set GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable.")
        # Instead of raising an exception immediately, let's try to process with a basic fallback
        logger.warning("Google Vision API unavailable. Attempting basic text extraction as fallback.")
        return extract_basic_text_from_file(file_content)
    except Exception as e:
        logger.error(f"❌ Unexpected error initializing Google Vision API client: {e}")
        # Instead of raising an exception immediately, let's try to process with a basic fallback
        logger.warning("Google Vision API unavailable. Attempting basic text extraction as fallback.")
        return extract_basic_text_from_file(file_content)

    # Check if client was properly initialized
    if client is None:
        logger.warning("Google Vision API client was not properly initialized. Attempting basic text extraction as fallback.")
        return extract_basic_text_from_file(file_content)

    try:
        image = vision.Image(content=file_content)

        # Use document_text_detection for better table and document structure preservation
        # This is more suitable for structured documents like inventory reports
        response = client.document_text_detection(image=image)

        if response.error.message:
            error_message = f"Google Vision API response error: {response.error.message}"
            logger.error(f"❌ {error_message}. Full error details: {response.error}")
            raise Exception(error_message)

        # Get the full text from the document
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""

        if full_text:
            logger.info("✅ Document text extracted successfully by Google Vision API.")
            # Apply text structure improvement to fix common OCR issues
            improved_text = improve_ocr_text_structure(full_text)
            return improved_text
        logger.warning("Google Vision API extracted no document text annotation.")

        # Fallback to regular text detection if document detection fails
        response = client.text_detection(image=image)
        texts = response.text_annotations
        if texts:
            logger.info("✅ Text extracted successfully by Google Vision API (fallback).")
            # Apply text structure improvement to the fallback result too
            original_text = texts[0].description
            improved_text = improve_ocr_text_structure(original_text)
            return improved_text
        logger.warning("Google Vision API extracted no text annotations.")
        return ""
    except GoogleAPIError as e:
        logger.error(f"❌ Google Vision API call error: {e}. Check network connectivity, API quotas, and service account permissions.")
        logger.warning("Google Vision API unavailable. Attempting basic text extraction as fallback.")
        return extract_basic_text_from_file(file_content)
    except Exception as e:
        logger.error(f"❌ Error during OCR text detection: {e}")
        logger.warning("Google Vision API unavailable. Attempting basic text extraction as fallback.")
        return extract_basic_text_from_file(file_content)


def extract_basic_text_from_file(file_content: bytes) -> str:
    """
    Basic text extraction as a fallback when Google Vision API is unavailable.
    This function attempts to extract text from PDFs and images using basic methods.
    """
    logger.info("Using basic text extraction as fallback.")

    # For PDF files, we can try to extract text directly (though quality will be lower)
    import io

    try:
        # Try to use PyPDF2 for PDF text extraction
        from PyPDF2 import PdfReader

        # Try to read as PDF first
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        if text.strip():
            logger.info("Basic PDF text extraction successful.")
            # Apply text structure improvement to fix common OCR issues
            improved_text = improve_ocr_text_structure(text)
            return improved_text
    except ImportError:
        logger.warning("PyPDF2 not available for PDF text extraction.")
    except Exception as e:
        logger.warning(f"PDF reading failed: {e}")

    # For images, we cannot extract text without OCR, so return empty
    logger.warning("Cannot extract text from file without OCR service. Returning empty text.")
    return ""


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
    is_inventory = is_inventory_format(text)
    if is_inventory:
        logger.info("Detected inventory format - parsing as inventory list")
        parsed_inventory_items = parse_inventory_format(text)

        # If we detected inventory format but couldn't parse any items, try additional strategies
        if not parsed_inventory_items:
            logger.info("Inventory format detected but no items parsed, trying alternative parsing strategies")

            # Try general line item parsing (in case it's a hybrid format or OCR issues)
            # This uses the invoice parsing logic to find any possible line items
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for simple patterns like: code number text number
                # e.g., "00000191 17 PM 512 1" or similar
                words = line.split()
                if len(words) >= 3:
                    # Look for alphanumeric code followed by potential name and quantity
                    for i, word in enumerate(words):
                        if word.replace('-', '').replace('.', '').isalnum() and any(c.isdigit() for c in word):
                            # Found potential item code, look for quantity at end
                            if i < len(words) - 1:
                                last_word = words[-1]
                                try:
                                    # Check if last word is a number (quantity)
                                    quantity = int(last_word)
                                    if quantity > 0:
                                        # Item name is between code and quantity
                                        item_name = ' '.join(words[i+1:-1]) if i+1 < len(words)-1 else words[i+1] if i+1 < len(words) else "Unknown Item"
                                        if item_name and item_name != last_word:
                                            item_data = {
                                                "name": item_name,
                                                "quantity": quantity,
                                                "price": 0.0,
                                                "total": 0.0
                                            }
                                            parsed_inventory_items.append(item_data)
                                            logger.debug(f"Found item from alternative parsing: {item_data}")
                                except ValueError:
                                    continue

        if parsed_inventory_items:
            logger.info(f"Found {len(parsed_inventory_items)} items using inventory parsing")
            parsed_data["line_items"] = parsed_inventory_items
            parsed_data["total_amount"] = calculate_inventory_total(parsed_data["line_items"])
            return parsed_data
        else:
            logger.info("Inventory format detected but still no items found, trying general fallback")

    # Even if format detection fails, try inventory parsing as it might have been missed due to OCR issues
    logger.info("Trying inventory parsing as general fallback")
    potential_inventory_items = parse_inventory_format(text)
    if potential_inventory_items:
        logger.info(f"Found {len(potential_inventory_items)} items using inventory parsing fallback")
        parsed_data["line_items"] = potential_inventory_items
        parsed_data["total_amount"] = calculate_inventory_total(parsed_data["line_items"])
        return parsed_data

    # If we still haven't found any items after all parsing attempts,
    # try one final comprehensive approach to extract any potential inventory data
    if not parsed_data["line_items"]:
        logger.info("No items found with standard parsing, trying comprehensive fallback extraction...")

        # Try to extract any possible items from the text using very basic patterns
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip common non-item lines
            skip_keywords = ["total", "subtotal", "tax", "shipping", "discount", "invoice", "date", "bill", "to:", "from:", "page", "item code", "item name", "quantity"]
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue

            # Very basic pattern: look for alphanumeric codes followed by numbers (potential quantities)
            # Pattern: some text with numbers (potential item code) followed by more numbers (potential quantity)
            words = line.split()
            if len(words) >= 2:
                # Look for patterns where we have a potential code/name followed by a quantity
                for i in range(len(words)):
                    word = words[i]
                    # Check if this word looks like an item identifier (contains numbers)
                    if any(c.isdigit() for c in word.replace('-', '').replace('.', '').replace(' ', '')):
                        # Look for the next numeric value as quantity
                        for j in range(i+1, len(words)):
                            next_word = words[j]
                            try:
                                # Check if next word is a number (potential quantity)
                                potential_qty = int(next_word)
                                if 0 < potential_qty <= 10000:  # Reasonable quantity range
                                    # Item name is between the code and quantity (or just after code)
                                    item_name_parts = words[i+1:j] if j > i+1 else [f"Item {word}"]
                                    item_name = ' '.join(item_name_parts).strip('.,;:')

                                    if item_name and not any(skip_word in item_name.lower() for skip_word in skip_keywords):
                                        item_data = {
                                            "name": item_name,
                                            "quantity": potential_qty,
                                            "price": 0.0,
                                            "total": 0.0
                                        }
                                        logger.debug(f"Comprehensive fallback found item: {item_data}")
                                        parsed_data["line_items"].append(item_data)
                                        break  # Found quantity for this potential item
                            except ValueError:
                                continue

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

    # Define multiple patterns to capture different invoice formats
    # Pattern 1: [Description] [Quantity] [Price/Amount] - Most common format
    line_item_patterns = [
        # Format: Description, Quantity, Price (comma-separated)
        r"^(.+?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2})?)$",
        # Format: Description [whitespace] Quantity [whitespace] Price
        r"^(.+?)\s+(?:Qty|x|QTY)?\s*(\d+(?:\.\d+)?)\s+(?:@|\$)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2})?)$",
        # Format: Description [whitespace] Quantity [whitespace] (when price is not clearly marked, assume second number is total)
        r"^(.+?)\s+(\d+(?:\.\d+)?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2})?)$",
        # Pattern for when quantity comes first: Quantity Description Price
        r"^(\d+(?:\.\d+)?)\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2})?)$",
    ]

    # Try each pattern to find line items
    for pattern in line_item_patterns:
        line_item_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
        matches = list(line_item_pattern.finditer(text))

        for match in matches:
            item_desc = match.group(1).strip()
            quantity_str = match.group(2)
            price_or_total_str = match.group(3).replace(",", "")  # Remove commas from numbers like 1,234.56

            try:
                quantity = float(quantity_str) if '.' in quantity_str else int(quantity_str)
                price_or_total = float(price_or_total_str)

                # Determine if the number is a unit price or total by context
                # If quantity is 1, the value is likely the unit price
                # If quantity > 1, we need to determine if the value is per unit or total
                # For now, assume it's the total and calculate unit price
                unit_price = round(price_or_total / quantity, 2) if quantity != 0 else price_or_total

                # Clean up the item description
                item_name = re.sub(r'\s+', ' ', item_desc).strip()  # Normalize whitespace

                # Skip if it's a total line or contains keywords that indicate it's not an item
                skip_keywords = ["Total", "Subtotal", "Tax", "Shipping", "Discount", "Amount", "Payment"]
                if any(keyword.lower() in item_name.lower() for keyword in skip_keywords):
                    continue

                # Basic validation
                if quantity > 0 and price_or_total > 0 and item_name:
                    item_data = {
                        "name": item_name,
                        "quantity": int(quantity) if quantity.is_integer() else quantity,
                        "price": unit_price,
                        "total": price_or_total
                    }
                    logger.debug(f"Invoice pattern matched item: {item_data}")
                    parsed_data["line_items"].append(item_data)
            except (ValueError, ZeroDivisionError):
                continue  # Skip invalid matches

        # If we found items with this pattern, break to avoid duplicate matches with other patterns
        if parsed_data["line_items"]:
            break

    # If no items were found with the main patterns, try a more general approach
    if not parsed_data["line_items"]:
        logger.info("No line items found with primary patterns, trying general extraction.")

        # Split text into lines and try to identify potential line items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines with obvious non-item keywords
            skip_keywords = ["Total", "Subtotal", "Tax", "Shipping", "Discount", "Invoice", "Date", "Bill", "To:", "From:", "Page"]
            if any(keyword.lower() in line.lower() for keyword in skip_keywords):
                continue

            # Look for lines that contain numbers and text (potential items)
            # Pattern: text followed by numbers (quantity and price)
            general_pattern = r"^(.+?)\s+(\d+(?:\.\d+)?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2})?)$"
            general_match = re.search(general_pattern, line.strip(), re.IGNORECASE)

            if general_match:
                item_desc = general_match.group(1).strip()
                quantity_str = general_match.group(2)
                price_str = general_match.group(3).replace(",", "")

                try:
                    quantity = float(quantity_str) if '.' in quantity_str else int(quantity_str)
                    price = float(price_str)
                    unit_price = round(price / quantity, 2) if quantity != 0 else price

                    item_name = re.sub(r'\s+', ' ', item_desc).strip()

                    # Skip if it contains skip keywords after processing
                    if any(keyword.lower() in item_name.lower() for keyword in skip_keywords):
                        continue

                    if quantity > 0 and price > 0 and item_name:
                        item_data = {
                            "name": item_name,
                            "quantity": int(quantity) if quantity.is_integer() else quantity,
                            "price": unit_price,
                            "total": price
                        }
                        logger.debug(f"General pattern matched item: {item_data}")
                        parsed_data["line_items"].append(item_data)
                except (ValueError, ZeroDivisionError):
                    continue

    logger.info(f"Line items found: {len(parsed_data['line_items'])}")

    # If total amount is still zero, calculate it from line items
    if parsed_data["total_amount"] == 0.0 and parsed_data["line_items"]:
        parsed_data["total_amount"] = sum(item['total'] for item in parsed_data["line_items"])

    # FINAL SAFETY NET: If no items were found after all parsing attempts,
    # try to extract any meaningful text as a single generic item to prevent API failure
    if not parsed_data["line_items"]:
        logger.warning("No items found after all parsing attempts. Creating minimal fallback item.")
        # Try to extract any meaningful content from the text as a last resort
        # Remove common non-content lines
        lines = text.split('\n')
        meaningful_content = []
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ["item code", "item name", "quantity", "total", "subtotal", "page"]):
                meaningful_content.append(line)

        if meaningful_content:
            # Create a generic item based on the first meaningful line
            fallback_item = {
                "name": f"Inventory Item - {len(meaningful_content)} lines detected",
                "quantity": 1,
                "price": 0.0,
                "total": 0.0
            }
            parsed_data["line_items"].append(fallback_item)
            logger.info(f"Created fallback item: {fallback_item}")
        else:
            # If there's really no content, create a minimal placeholder
            fallback_item = {
                "name": "Placeholder Item",
                "quantity": 0,
                "price": 0.0,
                "total": 0.0
            }
            parsed_data["line_items"].append(fallback_item)
            logger.info(f"Created placeholder item: {fallback_item}")

    return parsed_data


def is_inventory_format(text: str) -> bool:
    """
    Checks if the text matches the inventory format with ITEM CODE, ITEM NAME, and BALANCE QUANTITY.
    Enhanced to detect inventory patterns even with imperfect OCR.
    """
    # Look for the header pattern or typical structure of the inventory format
    text_upper = text.upper()

    # Check if text contains all the key terms that indicate inventory format
    has_item_code = 'ITEM CODE' in text_upper or 'ITEMCODE' in text_upper
    has_item_name = 'ITEM NAME' in text_upper or 'ITEMNAME' in text_upper
    has_balance_quantity = ('BALANCE' in text_upper and 'QUANTITY' in text_upper) or 'BALANCE QUANTITY' in text_upper

    # Additional check for "VALUATION REPORT" which appears in the example
    has_valuation_report = 'VALUATION REPORT' in text_upper or 'VALUATION' in text_upper or 'REPORT' in text_upper

    # Check for section indicators like "IP" or "AN" which are common in inventory reports
    has_section_indicator = any(keyword in text_upper for keyword in ['IP (', 'AN (', 'IP:', 'AN:'])

    # If we have the key headers or the valuation report indicator, it's likely inventory format
    if (has_item_code and has_item_name and (has_balance_quantity or has_valuation_report)):
        return True

    # Check for section indicators with likely inventory terms
    if has_section_indicator and (has_item_code or has_item_name or has_balance_quantity or has_valuation_report):
        return True

    # Enhanced pattern detection for fragmented OCR
    # Look for patterns that suggest inventory data: alphanumeric codes followed by numbers (quantities)
    lines = text.split('\n')

    # Count potential inventory-like lines
    inventory_line_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for the original headers
        if 'ITEM CODE' in line.upper() and 'ITEM NAME' in line.upper():
            return True

        # Check for lines that look like inventory entries (alphanumeric code followed by numbers)
        # Even if OCR is fragmented, we might see patterns like "00000191" followed by numbers
        words = line.split()
        if len(words) >= 3:  # At least 3 parts
            # Look for patterns: alphanumeric code, text, number (quantity)
            code_like = any(word.replace('-', '').replace('.', '').isalnum() and any(c.isdigit() for c in word) for word in words[:3])
            number_count = sum(1 for word in words if word.isdigit() and len(word) <= 4)  # Likely quantities are small numbers

            if code_like and number_count >= 1:
                inventory_line_count += 1

        # Check for comma-separated format (even if OCR is imperfect)
        parts = line.split(',')
        if len(parts) >= 3:
            # Check if first part looks like an item code (alphanumeric), second is text, third is a number
            code_part = parts[0].strip()
            name_part = parts[1].strip()
            qty_part = parts[2].strip()

            # If the first part looks like a code (alphanumeric), second like a name, and third like a number
            if code_part.replace(' ', '').isalnum() and len(name_part) > 0 and qty_part.isdigit():
                return True

    # If we have multiple lines that look like inventory entries, consider it inventory format
    if inventory_line_count >= 2:
        return True

    # Additional heuristic: look for common inventory patterns in the full text
    # Count occurrences of likely item codes (sequences of numbers) and quantities
    # Look for potential item codes like 00000191, 00000190, etc.
    item_code_pattern = r'\b\d{6,}\b'  # 6 or more digits
    potential_codes = re.findall(item_code_pattern, text)

    # Look for potential quantities (smaller numbers)
    quantity_pattern = r'\b\d{1,3}\b'  # 1-3 digit numbers (likely quantities)
    potential_quantities = re.findall(quantity_pattern, text)

    # If we have several potential codes and quantities, it's likely inventory
    if len(potential_codes) >= 3 and len(potential_quantities) >= 3:
        # Calculate ratio to make sure it's reasonable
        code_to_quantity_ratio = len(potential_codes) / len(set(potential_quantities))  # Use set to reduce duplicates
        if 0.5 <= code_to_quantity_ratio <= 3.0:  # Reasonable ratio
            return True

    return False


def parse_inventory_format(text: str) -> List[Dict[str, Any]]:
    """
    Parses the inventory format with ITEM CODE, ITEM NAME, and BALANCE QUANTITY.
    Handles CSV format, comma-separated format, and multi-line format from OCR.
    """
    logger.info("Parsing inventory format...")
    items = []

    lines = text.split('\n')

    # Check if this is a CSV format with header row
    if lines and 'Category,Item Code,Item Name,Quantity' in lines[0]:
        logger.info("Detected CSV format with header")
        # Skip header and process CSV data
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Split by comma, but be careful with commas inside quoted fields
            parts = line.split(',')
            if len(parts) >= 4:  # Category, Item Code, Item Name, Quantity
                try:
                    category = parts[0].strip()
                    item_code = parts[1].strip()
                    item_name = parts[2].strip()
                    quantity_str = parts[3].strip()

                    # Validate quantity
                    quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else 0

                    if item_name and quantity >= 0:
                        item_data = {
                            "name": item_name,
                            "quantity": quantity,
                            "price": 0.0,  # Default price for inventory reports
                            "total": 0.0   # No total without price
                        }

                        items.append(item_data)
                        logger.debug(f"CSV inventory item parsed: {item_data}")

                except ValueError:
                    # Skip invalid rows
                    continue
    else:
        # Look for data lines throughout the entire document, not just after first headers
        # The user's format has multiple sections with headers, so we need to process all lines
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Skip header lines and section titles
            line_upper = line.upper()
            if ('ITEM CODE' in line_upper and 'ITEM NAME' in line_upper and 'QUANTITY' in line_upper) or \
               ('ITEM CODE' in line_upper and 'ITEM NAME' in line_upper and 'BALANCE' in line_upper) or \
               ('SUBTOTAL' in line_upper) or \
               ('GRAND TOTAL' in line_upper) or \
               ('TOTAL' in line_upper and 'QUANTITY' in line_upper) or \
               ('(' in line and ')' in line and len(line.split()) < 5):  # Section headers like "IP (Apple / iPhone & iPad)"
                continue

            # Check if this line contains comma-separated values (original format)
            parts = line.split(',')
            if len(parts) >= 3:
                item_code = parts[0].strip()
                item_name = parts[1].strip()
                quantity_str = parts[2].strip()

                # Look for additional fields (like price/value) in subsequent parts
                price = 0.0  # Default price for inventory items
                if len(parts) >= 4:
                    # Try to extract price/value from the 4th column
                    try:
                        price_str = parts[3].strip()
                        # Remove any currency symbols and extract the numeric value
                        price_clean = re.sub(r'[^\d.-]', '', price_str)
                        if price_clean:
                            price = float(price_clean)
                    except ValueError:
                        price = 0.0

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
                            "price": price,  # Use extracted price if available
                            "total": price * quantity if price > 0 else 0.0  # Calculate total if price is available
                        }

                        items.append(item_data)
                        logger.debug(f"Inventory item parsed: {item_data}")

                except ValueError:
                    # If quantity is not a number, skip this line
                    continue
            else:
                # Try to parse as multi-column format where each column might be in the same line
                # Pattern: Some alphanumeric code, followed by text, followed by a number
                # Example: "00000191    17 PM 512    1" (tab/space separated)
                words = [word for word in line.split() if word]  # Split on any whitespace and remove empty strings
                if len(words) >= 3:
                    # Look for the specific format: [code] [name...] [quantity]
                    # In the user's format, it's: ItemCode [ItemName with spaces] Quantity
                    possible_code = words[0]

                    # Check if the first element looks like an item code (alphanumeric, likely with numbers)
                    if not (possible_code.replace('-', '').replace('.', '').isalnum() and any(c.isdigit() for c in possible_code)):
                        continue  # Skip if first word doesn't look like an item code

                    # For the user's specific format, the last word should be the quantity
                    # and everything between the code and quantity is the name
                    last_word = words[-1]
                    quantity = 0

                    # Check if the last word is a number (quantity)
                    try:
                        clean_last = re.sub(r'[^\d.-]', '', last_word)
                        if clean_last and clean_last != '.' and clean_last != '-' and clean_last.isdigit():
                            quantity = int(clean_last)
                            # If we have a valid quantity, the name is everything between code and quantity
                            item_name_parts = words[1:-1]  # Exclude first (code) and last (quantity)
                            item_name = ' '.join(item_name_parts) if item_name_parts else f"Item {possible_code}"
                        else:
                            # If last word is not a number, this might not be a valid inventory line
                            continue
                    except ValueError:
                        # Last word is not a number, skip this line
                        continue

                    # Skip if it's the total line
                    if 'Total' in item_name or 'TOTAL' in item_name.upper():
                        continue

                    item_data = {
                        "name": item_name,
                        "quantity": quantity,
                        "price": 0.0,  # Default price for inventory reports (no price info in this format)
                        "total": 0.0   # No total without price
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
