import google.generativeai as genai
import os
import asyncio
import traceback
import logging
from pathlib import Path
from uuid import UUID
from dotenv import load_dotenv
from database import SessionLocal
import crud

# ============================
# Configure Logging & Env
# ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Explicitly load .env from the same directory
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    logger.info(f"✅ [WhatsApp Agent] Loaded .env from {env_path}")
else:
    logger.warning(f"⚠️ [WhatsApp Agent] .env file not found at {env_path}")

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("✅ [WhatsApp Agent] Gemini API Configured")
else:
    logger.error("❌ [WhatsApp Agent] GEMINI_API_KEY not found in environment!")

# Session Store
chat_sessions = {}

# ============================
# 1. Product Lookup Tool
# ============================
def _get_product_details_logic(
    user_id: UUID | None,
    company_id: UUID | None,
    product_name: str | None = None,
    product_id: str | None = None
) -> dict:
    """
    Internal logic to get product details.
    STRICT RULE: company_id is MANDATORY. Data is filtered by this ID.
    """
    logger.info(f"--- AGENT: Product Lookup --- Context -> User: {user_id} | Company: {company_id} | Query: {product_name} / {product_id}")
    
    if not company_id:
        logger.error("❌ ERROR: Missing Company ID. Cannot perform isolated search.")
        return {"status": "NOT AVAILABLE (System Error: Company context missing)"}

    db = SessionLocal()
    try:
        product = None
        
        if product_id:
            p_uuid = UUID(product_id) if isinstance(product_id, str) else product_id
            product = crud.get_product(db, product_id=p_uuid, user_id=user_id, company_id=company_id)
        
        elif product_name:
            product = crud.get_product_by_name(db, name=product_name, company_id=company_id, user_id=user_id)
        
        else:
            return {"status": "NOT AVAILABLE (Please provide product_name or product_id)"}

        if not product:
            return {"status": "NOT AVAILABLE (Product not found in this company's inventory)"}
            
        stock_quantity = getattr(product, 'stock_quantity', 0)
        sale_price = getattr(product, 'sale_price', 0.0)
        
        product_details = {
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "sale_price": float(sale_price),
            "stock_quantity": stock_quantity,
            "unit": product.unit,
        }

        if stock_quantity <= 0:
            return {
                "status": "NOT AVAILABLE (Out of Stock)", 
                "details": product_details
            }
        else:
            return {
                "status": f"AVAILABLE. Price: {sale_price:.2f}. Details: {product.name} is in stock.", 
                "details": product_details
            }

    except Exception as e:
        logger.error(f"❌ ERROR in _get_product_details_logic: {e}")
        traceback.print_exc()
        return {"status": f"ERROR (System error during lookup)"}

    finally:
        db.close()

# ============================
# Agent Runner
# ============================
async def run_whatsapp_agent(message: str, phone_number: str, user_id: UUID | None, company_id: UUID | None) -> str:
    """
    Async wrapper that handles the chat logic.
    Ensures 'company_id' is passed to the tool for isolation.
    """
    # Reload API Key just in case
    global api_key
    if not api_key:
        logger.warning("⚠️ GEMINI_API_KEY missing in global scope. Reloading from env...")
        load_dotenv(dotenv_path=env_path, override=True)
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            logger.info("✅ GEMINI_API_KEY recovered.")
        else:
            logger.error("❌ CRITICAL: GEMINI_API_KEY still missing.")
            return "⚠️ Service Error: AI configuration missing. Please contact support."

    try:
        # 1. Create Chat Session if not exists
        if phone_number not in chat_sessions:
            
            def get_product_details(product_name: str | None = None, product_id: str | None = None):
                """
                Use this tool to search for a product in the inventory to check price and stock.
                Args:
                    product_name: The name of the item the customer is asking about.
                    product_id: Optional ID if provided.
                """
                if not company_id:
                    return {"status": "ERROR: No Company ID identified for this chat."}
                return _get_product_details_logic(user_id, company_id, product_name, product_id)

            tools_list = [get_product_details]
            
            # Dynamic Instructions
            db = SessionLocal()
            company_name = "BizzAuto"
            try:
                if company_id:
                    company = crud.get_company(db, company_id=company_id)
                    if company and company.name:
                        company_name = company.name
            except Exception as db_err:
                logger.error(f"DB Error fetching company: {db_err}")
            finally:
                db.close()

            tenant_system_instructions = f"""
            You are a friendly customer support representative for {company_name}.
            Your name is Sarah. You are chatting with a customer on WhatsApp.

            GOAL:
            Answer questions naturally and helpfully using the provided tools. Be conversational, not robotic.

            TONE & STYLE GUIDELINES:
            1. **Be Human:** Use phrases like "Let me check that for you," "Good news!", or "Oh, sorry about that."
            2. **Use Emojis:** Use friendly emojis occasionally (e.g., 👋, 🚗, ✅, 🔧).
            3. **Short & Sweet:** Keep messages easy to read on a phone screen.

            RULES FOR TOOLS:
            1. When asked about a product price or stock, YOU MUST use the `get_product_details` tool.
            2. **If Found (AVAILABLE):**
               - Say something like: "Yes, I checked and we have the **{{product_name}}** in stock! ✅ It's listed at **[Price]**."
               (Do NOT ask them to book or reserve it unless they explicitly ask).
            3. **If Not Found (NOT AVAILABLE / Out of Stock):**
               - Say: "I'm sorry, I just checked our inventory and it looks like we're out of stock for that item right now. 😔"
            4. **General Chat:** Reply naturally to Hi/Hello/Thanks.
            """

            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=tenant_system_instructions,
                tools=tools_list
            )
            
            chat_sessions[phone_number] = model.start_chat(
                enable_automatic_function_calling=True
            )
        
        chat = chat_sessions[phone_number]

        # 2. Run Gemini
        response = await asyncio.to_thread(chat.send_message, message)
        
        if not response.text:
             logger.warning(f"⚠️ Empty response text. Parts: {response.parts}")
             return "I'm having trouble finding the right words. Could you rephrase that?"

        return response.text

    except Exception as e:
        logger.error(f"❌ EXCEPTION in run_whatsapp_agent for {phone_number}: {e}")
        traceback.print_exc()
        # DISTINCT ERROR MESSAGE TO VERIFY CODE UPDATE
        return f"⚠️ SYSTEM ALERT: The AI Agent encountered an error: {str(e)}"
