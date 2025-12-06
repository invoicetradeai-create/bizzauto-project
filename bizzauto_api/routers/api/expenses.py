from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Union
from uuid import UUID
import json
from pydantic import BaseModel

# Imports from your project structure
from database import get_db
from models import Expense as PydanticExpense
from crud import (
    get_expense, get_expenses, create_expense, update_expense, delete_expense
)
from dependencies import set_rls_context, get_current_user
from sql_models import User
from whatsapp_utils import send_reply

router = APIRouter()

# --- 1. Pydantic Model for WhatsApp Payload ---
class ExpenseWhatsAppPayload(BaseModel):
    title: str = "New Expense" # Optional title
    amount: Union[float, int]
    category: str
    payment_method: str
    description: str
    date: str 
    phone: str 

# --- 2. CRUD Operations ---

@router.get("/", response_model=List[PydanticExpense])
@router.get("", response_model=List[PydanticExpense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_expenses(db, user_id=user.id, skip=skip, limit=limit)

@router.get("/{expense_id}", response_model=PydanticExpense)
def read_expense(expense_id: UUID, db: Session = Depends(set_rls_context)):
    db_expense = get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.post("/", response_model=PydanticExpense)
@router.post("", response_model=PydanticExpense) # Fix for 405 Error
def create_expense_route(expense: PydanticExpense, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Note: Ensure crud.create_expense excludes 'user_id' from model_dump inside crud.py
    return create_expense(db=db, expense=expense, user_id=user.id)

@router.put("/{expense_id}", response_model=PydanticExpense)
@router.put("/{expense_id}/", response_model=PydanticExpense)
def update_expense_route(expense_id: UUID, expense: PydanticExpense, db: Session = Depends(set_rls_context)):
    db_expense = update_expense(db=db, expense_id=expense_id, expense=expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/{expense_id}")
@router.delete("/{expense_id}/")
def delete_expense_route(expense_id: UUID, db: Session = Depends(set_rls_context)):
    db_expense = delete_expense(db=db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


# --- 3. WhatsApp Endpoint (With Template Fixes) ---

@router.post("/send-whatsapp", status_code=status.HTTP_200_OK)
@router.post("/send-whatsapp/", status_code=status.HTTP_200_OK)
async def send_expense_to_whatsapp(payload: ExpenseWhatsAppPayload, user: User = Depends(get_current_user)):
    # --- Backend Requirement 1: Print incoming payload ---
    print(f"📥 Hit /send-whatsapp with payload: {payload}")
    # --- End Backend Requirement 1 ---

    # --- Backend Requirement 2 & 3: Wrap entire logic in try/except and return 500 on exception ---
    try:
        """
        Sends expense details via WhatsApp Template 'expense_report'.
        Variables: {{1}}=Category, {{2}}=Amount, {{3}}=Payment Method, {{4}}=Date, {{5}}=Description
        """
        
        # --- Validations ---
        if not payload.phone:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        if payload.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        # Format amount with commas (e.g. 12,300.00)
        formatted_amount = f"{payload.amount:,.2f}"

        # Construct the Template Payload
        template_payload = {
            "type": "template",
            "template": {
                "name": "expense_report", # Exact match with Meta
                "language": {
                    "code": "en" # Try 'en', 'en_US', or 'en_GB' if 'en' fails
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": str(payload.category)       # {{1}} Category
                            },
                            {
                                "type": "text",
                                "text": formatted_amount            # {{2}} Amount
                            },
                            {
                                "type": "text",
                                "text": str(payload.payment_method) # {{3}} Payment Method
                            },
                            {
                                "type": "text",
                                "text": str(payload.date)           # {{4}} Date
                            },
                            {
                                "type": "text",
                                "text": str(payload.description)    # {{5}} Description
                            }
                        ]
                    }
                ]
            }
        }

        # Debugging: Print Payload
        print("\n--- 📤 Sending WhatsApp Payload ---")
        print(json.dumps(template_payload, indent=2))
        print("-----------------------------------\n")

        # Call Utility Function
        try: # This inner try/except block handles specific send_reply errors
            whatsapp_response = await send_reply(to=payload.phone, data=template_payload)
        except Exception as e:
            print(f"❌ Error calling send_reply: {str(e)}")
            # Raise an HTTPException here so the outer except block catches it
            raise HTTPException(status_code=500, detail=f"Failed to initiate WhatsApp sending: {str(e)}")

        # Handle Response
        if whatsapp_response and "messages" in whatsapp_response:
            print("✅ WhatsApp Sent Successfully")
            return {
                "status": "success",
                "message": "Expense report sent to WhatsApp",
                "meta_response": whatsapp_response
            }
        
        # If Meta returned an error inside the JSON
        if whatsapp_response and "error" in whatsapp_response:
            error_msg = whatsapp_response.get("error", {}).get("message", "Unknown Meta Error")
            print(f"⚠️ Meta API Error: {error_msg}")
            raise HTTPException(status_code=400, detail=f"WhatsApp API Error: {error_msg}")

        # Fallback for unknown states
        raise HTTPException(status_code=500, detail="Failed to send message (Unknown response from Meta)")

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly to be handled by FastAPI's HTTPException handler
        raise http_exc
    except Exception as e:
        # Catch any other unexpected exceptions and return a 500
        print(f"🚨 Unhandled exception in send_expense_to_whatsapp: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")