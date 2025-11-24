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
                    company_id=company_id,
                    client_id=parsed_data["client_id"],
                    total_amount=parsed_data["total_amount"]
                )
                db_invoice = create_invoice(db=db, invoice=invoice_data)
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


def parse_invoice_text(text, db, company_id):
    """
    Parse OCR text to extract client, items and total_amount.
    This is a simplified and robust implementation to avoid syntax issues.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        print("No text to parse.")
        return None

    # 1) Find client
    client_name = None
    for i, line in enumerate(lines):
        if "bill to" in line.lower():
            # next non-empty line is client
            if i + 1 < len(lines):
                client_name = lines[i + 1].strip()
            break
    if not client_name:
        # Try heuristics: look for common labels
        for i, line in enumerate(lines):
            if line.lower().startswith("client") or line.lower().startswith("customer"):
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    client_name = parts[1].strip()
                    break

    if not client_name:
        print("Client name not found.")
        return None

    client = get_client_by_name(db, name=client_name)
    if not client:
        print(f"Client '{client_name}' not found in database.")
        return None

    # 2) Find items block bounds
    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        if "description" in line.lower() or "item" == line.lower().strip():
            start_index = i + 1
            break
    # fallback: look for first numbered line
    if start_index is None:
        for i, line in enumerate(lines):
            if re.match(r'^\d+[\.\)]?\s+', line):
                start_index = i
                break
    # find subtotal or total as end
    for i, line in enumerate(lines):
        if "subtotal" in line.lower() or "sub total" in line.lower() or "subotal" in line.lower():
            end_index = i
            break
    if end_index is None:
        # fallback: find a line that looks like "total" near the end
        for i in range(len(lines)-1, -1, -1):
            if line := lines[i]:
                if "total" in line.lower():
                    end_index = i
                    break
    if start_index is None:
        start_index = 0
    if end_index is None or end_index <= start_index:
        end_index = len(lines)

    item_section = lines[start_index:end_index]
    if not item_section:
        print("No item section detected.")
        return None

    items = []

    i = 0
    while i < len(item_section):
        line = item_section[i]
        # detect numbered item or line that looks like a description
        if re.match(r'^\d+[\.\)]?\s+', line):
            description = re.sub(r'^\d+[\.\)]?\s*', '', line).strip()
            prices = []
            j = i + 1
            while j < len(item_section):
                nxt = item_section[j]
                if re.match(r'^\d+[\.\)]?\s+', nxt):
                    break
                # extract any price-like numbers from the line
                price_matches = re.findall(r'[\$]?\d{1,3}(?:[,]\d{3})*(?:\.\d+)?|\d+\.\d+', nxt)
                if price_matches:
                    for pm in price_matches:
                        p = _parse_price_from_text(pm)
                        if p is not None:
                            prices.append(p)
                else:
                    # append to description if no prices found
                    if nxt and not re.match(r'^[\-\—]{1,}$', nxt):
                        description += " " + nxt
                j += 1

            # decide unit_price, total, quantity
            if prices:
                total = prices[-1]
                unit_price = prices[-2] if len(prices) >= 2 else total
                quantity = 1
                if unit_price and unit_price > 0:
                    quantity = max(1, round(total / unit_price))
                
                item_data = {
                    "description": description.strip(),
                    "quantity": quantity,
                    "price": unit_price,
                    "total": total
                }
                process_item(item_data, items, db)
            else:
                print(f"⚠ Skipping line (no prices found): '{description}'")

            i = j
        else:
            # line without leading number: try to parse it as an item with inline prices
            price_matches = re.findall(r'[\$]?\d{1,3}(?:[,]\d{3})*(?:\.\d+)?|\d+\.\d+', line)
            if price_matches:
                # try to split description and prices
                # assume description is part before the first price match
                first_price_pos = re.search(r'[\$]?\d', line)
                if first_price_pos:
                    desc = line[:first_price_pos.start()].strip()
                    prices = []
                    for pm in price_matches:
                        p = _parse_price_from_text(pm)
                        if p is not None:
                            prices.append(p)
                    if prices:
                        total = prices[-1]
                        unit_price = prices[-2] if len(prices) >= 2 else total
                        quantity = 1
                        if unit_price and unit_price > 0:
                            quantity = max(1, round(total / unit_price))
                        
                        item_data = {
                            "description": desc,
                            "quantity": quantity,
                            "price": unit_price,
                            "total": total
                        }
                        process_item(item_data, items, db)

            i += 1

    # 3) Extract total amount (look from bottom up for 'total' not 'subtotal')
    total_amount = 0.0
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if "subtotal" in line.lower() or "subotal" in line.lower():
            continue
        if "total" in line.lower():
            # Check on the same line
            pm = re.search(r'[\$]?([\d,]+\.\d+|[\d,]+)', line)
            if pm:
                try:
                    total_amount = float(pm.group(1).replace(',', ''))
                    break
                except Exception:
                    pass
            # Check on the next line
            if i + 1 < len(lines):
                next_line = lines[i+1]
                pm = re.search(r'[\$]?([\d,]+\.\d+|[\d,]+)', next_line)
                if pm:
                    try:
                        total_amount = float(pm.group(1).replace(',', ''))
                        break
                    except Exception:
                        pass

    if not items:
        print("No invoice items could be parsed from the text.")
        return None

    print(f"Successfully parsed {len(items)} items with total ${total_amount}")
    return {
        "client_id": client.id,
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
        print(f"✗ Product '{description}' not found in database")