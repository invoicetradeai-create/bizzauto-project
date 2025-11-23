import openai
print("OpenAI version:", openai.__version__)

import pkgutil
print("Agents loaded?", pkgutil.find_loader("openai.agents"))

import os
import google.generativeai as genai
from uuid import UUID
from database import SessionLocal
import crud

# Configure the Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# In-memory store for chat histories
chat_sessions = {}

# Tool Definition
def get_product_details(
    product_name: str | None = None,
    product_id: str | None = None
) -> dict:
    """
    Retrieve details of a product from the database.
    """
    db = SessionLocal()
    try:
        if product_id:
            product = crud.get_product(db, product_id=UUID(product_id))
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
    finally:
        db.close()

# Create a generative model with the tool
model = genai.GenerativeModel(
    model_name='gemini-pro',
    tools=[get_product_details]
)

# Main function to run the agent
async def run_whatsapp_agent(message: str, phone_number: str) -> str:
    """
    Runs the Gemini agent with chat history.
    """
    if phone_number not in chat_sessions:
        chat_sessions[phone_number] = model.start_chat()

    chat = chat_sessions[phone_number]
    response = await chat.send_message_async(message)
    return response.text
