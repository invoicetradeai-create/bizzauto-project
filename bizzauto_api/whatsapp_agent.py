import google.generativeai as genai
import os
import asyncio
import traceback
from uuid import UUID
from database import SessionLocal
import crud

# ============================
# 1. Product Lookup Tool (Strict Isolation Logic)
# ============================
def _get_product_details_logic(
    user_id: UUID | None,
    company_id: UUID | None,
    product_name: str | None = None,
    product_id: str | None = None # Changed to str to handle UUID input from AI
) -> dict:
    """
    Internal logic to get product details.
    STRICT RULE: company_id is MANDATORY. Data is filtered by this ID.
    """
    print(f"--- AGENT: Product Lookup ---")
    print(f"Context -> User: {user_id} | Company: {company_id}")
    print(f"Query   -> Name: {product_name} | ID: {product_id}")
    
    # 1. Strict Isolation Check
    if not company_id:
        print("❌ ERROR: Missing Company ID. Cannot perform isolated search.")
        return {"status": "NOT AVAILABLE (System Error: Company context missing)"}

    db = SessionLocal()
    try:
        product = None
        
        # 2. Fetch Product (Scoped to Company)
        if product_id:
            # Convert string to UUID if necessary
            p_uuid = UUID(product_id) if isinstance(product_id, str) else product_id
            product = crud.get_product(db, product_id=p_uuid, user_id=user_id, company_id=company_id)
        
        elif product_name:
            # THIS IS THE KEY: We pass company_id to the CRUD layer
            product = crud.get_product_by_name(db, name=product_name, company_id=company_id, user_id=user_id)
        
        else:
            return {"status": "NOT AVAILABLE (Please provide product_name or product_id)"}

        # 3. Handle 'Not Found'
        if not product:
            return {"status": "NOT AVAILABLE (Product not found in this company's inventory)"}
            
        # 4. Check Stock & Availability
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
        print(f"❌ ERROR in _get_product_details_logic: {e}")
        traceback.print_exc()
        return {"status": f"ERROR (System error during lookup)"}

    finally:
        db.close()

# ============================
# Configure Generative Model
# ============================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY is not set.")

genai.configure(api_key=api_key)



# Session Store
chat_sessions = {}

# ============================
# Agent Runner
# ============================
async def run_whatsapp_agent(message: str, phone_number: str, user_id: UUID | None, company_id: UUID | None) -> str:
    """
    Async wrapper that handles the chat logic.
    Ensures 'company_id' is passed to the tool for isolation.
    """
    try:
        # 1. Create Chat Session if not exists
        if phone_number not in chat_sessions:
            
            # --- Define Tool with Context Binding ---
            def get_product_details(product_name: str | None = None, product_id: str | None = None):
                """
                Use this to find product price and availability.
                Args:
                    product_name: Name of the item (e.g., 'Tyre', 'Oil').
                    product_id: Optional ID.
                """
                # Strict Context Check before calling logic
                if not company_id:
                    return {"status": "ERROR: No Company ID identified for this chat."}
                
                return _get_product_details_logic(user_id, company_id, product_name, product_id)

            tools_list = [get_product_details]
            
            # --- Dynamic System Instructions (Tenant-Specific) ---
            db = SessionLocal()
            company_name = "BizzAuto" # Default company name
            try:
                if company_id:
                    company = crud.get_company(db, company_id=company_id)
                    if company and company.name:
                        company_name = company.name
            finally:
                db.close()

            tenant_system_instructions = f"""
You are a helpful assistant for {company_name}.
Your goal is to answer questions strictly based on the provided tools.

RULES:
1. If a user asks about a product, YOU MUST use the `get_product_details` tool.
2. Do not guess product prices or availability. Rely ONLY on the tool output.
3. Check the tool's 'status':
   - If 'NOT AVAILABLE' (Out of Stock or Not Found): Politely tell the user the product is not available.
   - If 'AVAILABLE': Say "Yes, this product is available", mention the price, and ask if they want to order.
4. Keep responses concise and professional.
"""
            # Initialize Model
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction=tenant_system_instructions, # Use dynamic instructions
                tools=tools_list
            )
            
            chat_sessions[phone_number] = model.start_chat(
                enable_automatic_function_calling=True
            )
        
        chat = chat_sessions[phone_number]

        # 2. Run Gemini (Non-blocking)
        # Note: We pass the message and let the model decide to call the tool
        response = await asyncio.to_thread(chat.send_message, message)
        
        return response.text if response and response.text else "Sorry, I didn't understand that."

    except Exception as e:
        print(f"❌ ERROR inside run_whatsapp_agent for {phone_number}: {e}")
        traceback.print_exc()
        return "System is currently unavailable. Please try again later."