# agent.py
import os
import json
from uuid import UUID
from dotenv import load_dotenv, find_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, SQLiteSession

from database import SessionLocal
import crud


# Load env variables
load_dotenv(find_dotenv())

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================
# 1. Configure Gemini Client
# ============================
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# LLM Model Wrapper
llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)


# ============================
# 2. Product Lookup Tool
# ============================
@function_tool
def get_product_details(
    product_name: str | None = None,
    product_id: int | None = None
) -> dict:
    """
    Retrieve details of a product from the database.
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
# 3. Create Agent
# ============================
agent = Agent(
    name="whatsapp_product_agent",
    model=llm_model,
    tools=[get_product_details],
    instructions=(
        "You are a WhatsApp assistant for BizzAuto. "
        "When a user asks for product info, always call get_product_details. "
        "If a user asks about quantity, 'how many', or 'in stock', respond with the stock_quantity. "
        "If a user asks about price or 'how much', respond with the sale_price. "
        "Respond in short, friendly text."
    )
)


# ============================
# 4. Runner Wrapper (Async)
# ============================
async def run_whatsapp_agent(message: str, phone_number: str) -> str:
    """
    Now accepts phone_number to maintain unique chat history for each user.
    """
    # Create a persistent session object for the user (phone number)
    session = SQLiteSession(session_id=phone_number, db_path="whatsapp_sessions.db")
    
    result = await Runner.run(
        agent, 
        message, 
        session=session
    ) 
    return result.final_output


