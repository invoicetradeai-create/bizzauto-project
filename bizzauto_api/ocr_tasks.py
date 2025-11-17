import os
from google.cloud import vision
import io

# --- Google Cloud Vision API Setup ---
# IMPORTANT:
# 1. Make sure you have enabled the Cloud Vision API in your Google Cloud project.
# 2. Make sure you have downloaded a service account JSON key file.
# 3. Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of your JSON key file.
#    For example, in your terminal (on Linux/macOS):
#    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
#    In PowerShell (on Windows):
#    $env:GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

def process_invoice_image_gcp(image_path):
    """
    Processes an invoice image using Google Cloud Vision API, extracts text,
    and (in the future) creates an invoice record.
    """
    print(f"Processing image: {image_path}")

    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Use DOCUMENT_TEXT_DETECTION for dense text (like invoices)
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

        # TODO:
        # 1. Parse the 'full_text' to extract structured invoice data
        #    (e.g., invoice number, date, total amount, line items).
        # 2. Use the CRUD module to create a new invoice in the database.
        
        # For now, we just print the text.
        # Example of what the next step would look like:
        # from crud import create_invoice
        # from models import Invoice # Pydantic model
        # from database import SessionLocal
        # 
        # db = SessionLocal()
        # parsed_data = parse_invoice_text(full_text)
        # invoice = Invoice(**parsed_data)
        # create_invoice(db=db, invoice=invoice)
        # db.close()

        # Clean up the downloaded image file
        os.remove(image_path)
        print(f"Successfully processed and removed {image_path}")

        return full_text

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        # Optionally, move the file to an error directory instead of deleting
        return None

def parse_invoice_text(text):
    """
    A placeholder function to parse invoice text.
    This will need to be implemented with logic to find invoice fields.
    """
    # This is a very basic example. Real-world parsing is much more complex
    # and might require regular expressions or even a machine learning model.
    parsed_data = {
        "client_id": None,
        "total_amount": 0.0,
        # ... other fields from your invoice model
    }
    # ... parsing logic here ...
    return parsed_data
