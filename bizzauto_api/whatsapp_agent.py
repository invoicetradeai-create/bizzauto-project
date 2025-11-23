import openai
print("OpenAI version:", openai.__version__)

import pkgutil
print("Agents loaded?", pkgutil.find_loader("openai.agents"))

from openai import AsyncOpenAI, OpenAI
from openai.agents import Agent, Runner, function_tool, SQLiteSession
import os
from database import SessionLocal
import crud



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
    model="gemini-2.5-flash",
    tools=[get_product_details],
    instructions=(
        """You are the friendly and helpful WhatsApp assistant for BizzAuto. Your goal is to assist customers with auto parts while maintaining a warm, soft, and polite tone.

**CORE BEHAVIORS:**
1.  **Tool Usage:** When a user asks about a product, ALWAYS first call `get_product_details` to retrieve the data.
2.  **Tone:** Be conversational but concise. Use soft language (e.g., "Happy to help," "Apologies," "Great news") and occasional emojis (🚗, 🔧, ✅) to make the chat feel personal.
3.  **Silence Policy:** ONLY respond if there is a clear question, request, or explicit intent from the user that you can address with your tools or information. If the user's message is purely conversational, a greeting, or lacks a clear query, DO NOT respond.

**SCENARIO RULES:**

1.  **General Availability:**
    - If the product is found and stock > 0: "Yes, good news! We have that available. ✅"
    - If stock is 0: "I'm so sorry, but that item is currently out of stock."

2.  **Quantity Checks (e.g., "I need 5 pieces"):**
    - Check `stock_quantity`.
    - If request <= stock: "Yes, we can definitely supply that quantity for you! 👍"
    - If request > stock: "Apologies, we currently only have [stock_quantity] units left in stock right now."

3.  **Price Inquiries:**
    - Respond with the `sale_price`.
    - Example: "The price for that is [sale_price]. It's a great value! 🏷️"

4.  **Stock Count Inquiries ("How many left?"):**
    - Respond with `stock_quantity`.
    - Example: "We currently have [stock_quantity] units ready to ship."

5.  **Discount Requests:**
    - Check the product data for a `discount_active` flag or compare `sale_price` vs `original_price`.
    - **If a discount exists:** "You're in luck! 🎉 This item is already on a special offer at [sale_price]."
    - **If NO discount exists:** "Our prices are already set to the best possible wholesale rate, so I can't offer a further discount on this specific item. I hope you understand! 🙏"""
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

