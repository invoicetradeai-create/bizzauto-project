import google.generativeai as genai
import os
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
# 2. Configure Generative Model
# ============================
# Configure the Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

# Define the system instructions
system_instructions = (
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

# Create the GenerativeModel instance
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction=system_instructions,
    tools=[get_product_details]
)

# In-memory chat history
chat_sessions = {}

# ============================
# 3. Runner Wrapper (Async)
# ============================
async def run_whatsapp_agent(message: str, phone_number: str) -> str:
    """
    Accepts a message and phone_number to maintain a chat history for each user.
    Uses Gemini for function calling to respond to the user.
    """
    # Get or create a chat session for the user
    if phone_number not in chat_sessions:
        chat_sessions[phone_number] = model.start_chat()
    
    chat = chat_sessions[phone_number]

    # Send the user message to the model
    response = await chat.send_message_async(message)
    
    try:
        # Check if the model wants to call a function
        function_call = response.candidates[0].content.parts[0].function_call
        
        if function_call.name == 'get_product_details':
            # Extract arguments and call the actual function
            args = {key: value for key, value in function_call.args.items()}
            tool_result = get_product_details(**args)
            
            # Send the function's result back to the model
            response = await chat.send_message_async(
                genai.Part.from_function_response(
                    name='get_product_details',
                    response=tool_result,
                ),
            )

        # The final response from the model after the tool call
        return response.text

    except (ValueError, AttributeError):
        # This occurs if the response does not contain a function call.
        # It means the model responded directly with text.
        return response.text

    return "Sorry, I encountered an issue. Please try again."