import os
from google.cloud import vision
import io
import re
from uuid import UUID
from crud import get_client_by_name, get_product_by_name, create_invoice, create_invoice_item
from models import Invoice, InvoiceItem
from database import SessionLocal

# --- Google Cloud Vision API Setup ---
# IMPORTANT:
# 1. Make sure you have enabled the Cloud Vision API in your Google Cloud project.
# 2. Make sure you have downloaded a service account JSON key file.
# 3. Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of your JSON key file.
#    For example, in your terminal (on Linux/macOS):
#    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
#    In PowerShell (on Windows):
#    $env:GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

def process_invoice_image_gcp(gcs_uri, company_id: UUID):
    """
    Processes an invoice image from GCS using Google Cloud Vision API, extracts text,
    parses it, and creates an invoice record in the database.
    """
    print(f"Processing image from GCS: {gcs_uri}")

    try:
        client = vision.ImageAnnotatorClient()

        image = vision.Image()
        image.source.image_uri = gcs_uri # Use GCS URI
        
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        full_text = response.full_text_annotation.text
        print("--- Extracted Text ---")
        print(full_text)
        print("----------------------")

        db = SessionLocal()
        try:
            parsed_data = parse_invoice_text(full_text, db, company_id)
            
            if parsed_data and parsed_data.get("client_id") and parsed_data.get("items"):
                # Create Invoice
                invoice_data = Invoice(
                    client_id=parsed_data["client_id"],
                    total_amount=parsed_data["total_amount"]
                )
                db_invoice = create_invoice(db=db, invoice=invoice_data, company_id=company_id)
                print(f"Created invoice with ID: {db_invoice.id}")

                # Create Invoice Items
                for item in parsed_data["items"]:
                    if item.get("product_id"):
                        invoice_item_data = InvoiceItem(
                            invoice_id=db_invoice.id,
                            product_id=item["product_id"],
                            quantity=item["quantity"],
                            price=item["price"],
                            total=item["total"]
                        )
                        create_invoice_item(db=db, invoice_item=invoice_item_data)
                        print(f"Created invoice item for product ID: {item['product_id']}")
            else:
                print("Could not parse invoice data or find required fields.")

        finally:
            db.close()

        # No need to remove the file from local storage
        # You might want to add logic here to delete the file from GCS after processing

        return full_text

    except Exception as e:
        print(f"Error processing image {gcs_uri}: {e}")
        return None


def _parse_price_from_text(s):
    """Return float from a string like '$1,234.56' or '1234.56', or None."""
    if not s:
        return None
    m = re.search(r'[\$]?\s*([\d{1,3}[,\d]*\.?\d+]*)', s)
    # Fallback simpler regex
    m = re.search(r'[\$]?([\d,]+\.\d+|[\d,]+)', s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', ''))
    except Exception:
        return None


def extract_client_from_text(text_lines, db):
    """
    Tries to find a valid client in the database from the OCR text lines.
    """
    
    # Heuristics for client_name lines often directly below "BILL TO"
    try:
        bill_to_index = [i for i, line in enumerate(text_lines) if "bill to" in line.lower()][0]
        # Search lines after "BILL TO:"
        for i in range(bill_to_index + 1, min(bill_to_index + 4, len(text_lines))): # Check up to 3 lines
            candidate_name = text_lines[i].strip()
            if not candidate_name or "FROM:" in candidate_name.upper(): # Skip empty or "FROM:" line
                continue
            
            # Remove "Name: " prefix if present
            if candidate_name.lower().startswith("name:"):
                candidate_name = candidate_name[len("name:"):].strip()

            print(f"🔍 Checking if '{candidate_name}' is a valid client from BILL TO section...")
            client = get_client_by_name(db, candidate_name)
            if client:
                print(f"✅ Found client: {client.name}")
                return client.id
    except IndexError:
        pass # "BILL TO" not found, proceed to other heuristics

    # If not found directly below "BILL TO", try a more general search for lines that look like a client name
    # starting from the beginning of the text
    for line in text_lines:
        candidate_name = line.strip()
        # Skip common invoice parts or very short strings
        if not candidate_name or len(candidate_name) < 3 or any(keyword in candidate_name.upper() for keyword in ["INVOICE", "DETAILS", "ID:", "DATE:", "STATUS:", "ITEM", "QTY", "TOTAL"]):
            continue
        
        # Remove "Name: " prefix if present
        if candidate_name.lower().startswith("name:"):
            candidate_name = candidate_name[len("name:"):].strip()

        print(f"🔍 Checking if '{candidate_name}' is a valid client from general text...")
        client = get_client_by_name(db, candidate_name)
        if client:
            print(f"✅ Found client: {client.name}")
            return client.id
            
    return None

def parse_invoice_text(text, db, company_id):
    """
    Parse OCR text to extract client, items and total_amount.
    This is a simplified and robust implementation to avoid syntax issues.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        print("No text to parse.")
        return None

    # 1) Find client using the new helper function
    client_id = extract_client_from_text(lines, db)
    
    if not client_id:
        print("Client name not found or client not in database after advanced search.")
        return None

    # 2) Find items block bounds and parse them
    items = []
    try:
        # Find start of item section using common headers
        item_headers = ["description", "item", "charges", "service"]
        start_index = -1
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in item_headers):
                start_index = i + 1
                break
        
        if start_index == -1: raise ValueError("Item section start not found")

        # Find end of item section using common footers
        item_footers = ["subtotal", "sub total", "tax", "total", "amount due", "payment", "thank you"]
        end_index = len(lines)
        for i in range(start_index, len(lines)):
            if any(footer in lines[i].lower() for footer in item_footers):
                end_index = i
                break

        item_section_lines = lines[start_index:end_index]
        
        # --- State-Machine Parser for Line Items ---
        i = 0
        while i < len(item_section_lines):
            line = item_section_lines[i].strip()
            
            # Skip common headers
            if line.upper() in ["DESCRIPTION", "QTY", "PRICE", "AMOUNT"]:
                i += 1
                continue
            
            # Heuristic: If a line starts with a number, it's likely a quantity.
            # But if it's a long string with text, it's a description.
            # A good description line is mostly text.
            is_description_like = len(re.findall(r'[a-zA-Z]', line)) > len(re.findall(r'[\d\$\.]', line))

            if is_description_like and len(line) > 5: # Likely a description
                description = line
                # Look ahead for quantity, price, and amount on the next few lines
                prices = []
                qty = 1 # Default quantity
                
                # Check next 3 lines for numbers
                lookahead_index = i + 1
                while lookahead_index < min(i + 4, len(item_section_lines)):
                    next_line = item_section_lines[lookahead_index]
                    # Extract all numbers from the line
                    price_matches = re.findall(r'[\$]?\d{1,3}(?:[,]\d{3})*(?:\.\d+)?', next_line)
                    if price_matches:
                        for p_str in price_matches:
                            price_val = _parse_price_from_text(p_str)
                            if price_val is not None:
                                prices.append(price_val)
                    lookahead_index += 1
                
                if prices:
                    # Heuristic: largest number is total, second largest is price
                    prices.sort(reverse=True)
                    total = prices[0]
                    unit_price = prices[1] if len(prices) > 1 else total
                    
                    # Try to find quantity if it's among the numbers
                    potential_qtys = [p for p in prices if p < 100 and '.' not in str(p)] # Guess that qty is a small integer
                    if len(potential_qtys) == 1 and potential_qtys[0] > 0:
                        qty = int(potential_qtys[0])
                        # Recalculate unit_price if qty is found
                        if total / qty > 1:
                            unit_price = total / qty
                    elif unit_price > 0:
                         # Estimate qty if not explicitly found
                         estimated_qty = round(total/unit_price)
                         if estimated_qty > 0 : qty = estimated_qty


                    item_data = {
                        "description": description,
                        "quantity": qty,
                        "price": unit_price,
                        "total": total
                    }
                    process_item(item_data, items, db)
                    # We consumed the lookahead lines, so we can skip them
                    i = lookahead_index -1
                
            i += 1
            
    except Exception as e:
        print(f"Could not parse item section: {e}")
        pass # Allow parsing to continue for total amount

    # 3) Extract total amount
    total_amount = 0.0
    for line in reversed(lines): # Search from bottom up
        if "total" in line.lower() and "sub" not in line.lower():
            price_match = re.search(r'[\$]?\s*([\d,]+\.\d{2})', line)
            if price_match:
                try:
                    total_amount = float(price_match.group(1).replace(',', ''))
                    break # Stop after finding the first valid total from the bottom
                except (ValueError, IndexError):
                    continue
    
    if not items:
        print("No invoice items could be parsed from the text.")
        return None

    # If total amount wasn't found, calculate it from items
    if total_amount == 0.0:
        total_amount = sum(item.get('total', 0) for item in items)

    print(f"Successfully parsed {len(items)} items with total ${total_amount}")
    return {
        "client_id": client_id, # Use the client_id found earlier
        "items": items,
        "total_amount": total_amount
    }


def process_item(item_data, items_list, db):
    """
    Process a collected item-like dict (with description/prices or product_id).
    Adds a normalized item entry to items_list using DB lookup when possible.
    """
    # If already has product_id, just append
    if item_data.get("product_id"):
        items_list.append({
            "product_id": item_data["product_id"],
            "quantity": item_data.get("quantity", 1),
            "price": item_data.get("price", 0.0),
            "total": item_data.get("total", 0.0)
        })
        return

    description = item_data.get("description", "").strip()
    unit_price = item_data.get("price", 0.0)
    total = item_data.get("total", 0.0)
    quantity = item_data.get("quantity", 1)

    if not description:
        print("Skipping anonymous item (no description).")
        return

    if not total and unit_price:
        total = unit_price * quantity

    # lookup product
    product = get_product_by_name(db, name=description)
    if product:
        items_list.append({
            "product_id": product.id,
            "quantity": quantity,
            "price": unit_price,
            "total": total
        })
        print(f"✓ Matched to product ID: {product.id}")
    else:
        items_list.append({
            "product_id": None,
            "description": description,
            "quantity": quantity,
            "price": unit_price,
            "total": total
        })