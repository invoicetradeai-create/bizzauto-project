import google.generativeai as genai
import os
import asyncio
from database import SessionLocal
import crud
from uuid import UUID
import json

# ============================
# 1. Product Lookup Tool
# ============================
def get_product_details(
    product_name: str | None = None,
    product_id: int | None = None
) -> dict:
    """
    Use this function to get the details of a product, such as its price and availability.
    """

    db = SessionLocal()
    try:
        if product_id:
            product = crud.get_product(db, product_id=UUID(int=product_id))
        elif product_name:
            product = crud.get_product_by_name(db, name=product_name)
        else:
            return {"error": "Provide product_name or product_id"}

        if not product:
            return {"error": "Product not found"}

        return {
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "purchase_price": float(product.purchase_price),
            "sale_price": float(product.sale_price),
            "stock_quantity": product.stock_quantity,
            "low_stock_alert": product.low_stock_alert,
            "unit": product.unit,
        }

    except Exception as e:
        return {"error": f"Error fetching product: {str(e)}"}

    finally:
        db.close()

# ============================
# Configure Generative Model
# ============================
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# System instructions
system_instructions = """
You are a helpful and passive assistant for BizzAuto, a company that sells all kinds of wholesale and retailer products.
Your ONLY job is to answer direct questions from users.
- DO NOT initiate conversations or send proactive messages.
- If a user asks about a specific product, ALWAYS use the `get_product_details` tool to check for it.
- If the tool finds the product and it is in stock (stock_quantity > 0), reply with "Yes, we have [product name]! The price is [sale_price]."
- If the tool finds the product but it is out of stock (stock_quantity <= 0), reply with "Sorry, [product name] is currently out of stock."
- If the tool returns "Product not found", reply with "Sorry, I couldn't find a product by that name."
- For any other questions, provide a short and helpful answer.
- Keep all responses concise and to the point.
"""

tools_list = [get_product_details]

# Initialize Model
# NOTE: If 'gemini-1.5-flash' still gives 404 after pip install, change to 'gemini-pro'
model = genai.GenerativeModel(
    model_name='gemini-pro', 
    system_instruction=system_instructions,
    tools=tools_list
)

chat_sessions = {}

# ============================
# Runner Wrapper (Async Fixed)
# ============================
async def run_whatsapp_agent(message: str, phone_number: str) -> str:
    """
    Async wrapper that handles the chat logic
    """
    try:
        # 1. Create Chat Session if not exists
        if phone_number not in chat_sessions:
            chat_sessions[phone_number] = model.start_chat(
                enable_automatic_function_calling=True
            )
        
        chat = chat_sessions[phone_number]

        # 2. Run the blocking Gemini call in a thread to prevent blocking FastAPI
        # This fixes the "await" error while keeping the server responsive
        response = await asyncio.to_thread(chat.send_message, message)
        
        return response.text

    except Exception as e:
        # Log the actual error for debugging
        print(f"ERROR inside run_whatsapp_agent: {e}")
        
        # If the model name is wrong, catch it here
        if "404" in str(e) and "models/" in str(e):
            return "System Error: AI Model version mismatch. Please contact admin."
            
        return "Sorry, I'm having trouble connecting to the system right now. 🔧"
