Here are the code changes that have been applied to implement user-specific product filtering for the auto-reply feature.

**1. `bizzauto_api/crud.py`**
The `get_product` function was modified to include `user_id` in its parameters and filter products accordingly:

```python
def get_product(db: Session, product_id: UUID, user_id: UUID):
    return db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
```

**2. `bizzauto_api/whatsapp_agent.py`**
The `run_whatsapp_agent` function's signature was updated to make `user_id` a mandatory argument. The internal `_get_product_details_logic` already correctly uses this `user_id` for filtering.

```python
async def run_whatsapp_agent(message: str, phone_number: str, user_id: UUID) -> str:
    """
    Async wrapper that handles the chat logic
    """
    try:
        # 1. Create Chat Session if not exists
        if phone_number not in chat_sessions:
            
            # Create a tool bound to this user
            def get_product_details(product_name: str | None = None, product_id: int | None = None):
                """
                Use this function to get the details of a product, such as its price and availability.
                """
                if not user_id:
                    return {"error": "User context missing"}
                return _get_product_details_logic(user_id, product_name, product_id)

            tools_list = [get_product_details]
            
            # Initialize Model per session to bind the specific tool
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction=system_instructions,
                tools=tools_list
            )
            
            chat_sessions[phone_number] = model.start_chat(
                enable_automatic_function_calling=True
            )
        
        chat = chat_sessions[phone_number]

        # 2. Run the blocking Gemini call in a thread to prevent blocking FastAPI
        # This fixes the "await" error while keeping the server responsive
        response = await asyncio.to_thread(chat.send_message, message)
        
        # Ensure that response.text is always a string, even if empty or None
        return response.text if response and response.text is not None else ""

    except Exception as e:
        # Log the actual error for debugging
        print(f"ERROR inside run_whatsapp_agent for phone {phone_number}: {e}")
        traceback.print_exc() # Add full traceback
        
        # If the model name is wrong, catch it here
        if "404" in str(e) and "models/" in str(e):
            available_models = [m.name for m in genai.list_models()]
            print(f"DEBUG: Available models: {', '.join(available_models)}")
            return "System Error: AI Model (gemini-2.0-flash) not found or API key invalid. Please contact admin and check logs for available models."
            
        return "Sorry, I'm having trouble connecting to the system right now. 🔧"
```

**3. `bizzauto_api/routers/api/meta_whatsapp.py`**
The call to `run_whatsapp_agent` within the `process_whatsapp_message` function was updated to pass the `user_id` extracted from the message's context:

```python
                            if not user_id_for_log:
                                continue
                                
                            # --- 3. Run Agent (No DB Connection Held) ---
                            reply = await run_whatsapp_agent(incoming_text, sender_phone, user_id=user_id_for_log)
                            
                            if not reply:
                                continue
```

These changes ensure that the auto-reply logic now correctly filters products based on the user who sent the WhatsApp message.
