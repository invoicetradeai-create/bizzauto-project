from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Expense as PydanticExpense
from crud import (
    get_expense, get_expenses, create_expense, update_expense, delete_expense
)
from dependencies import set_rls_context, get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticExpense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expenses = get_expenses(db, user_id=user.id, skip=skip, limit=limit)
    return expenses

@router.get("/{expense_id}", response_model=PydanticExpense)
def read_expense(expense_id: UUID, db: Session = Depends(set_rls_context)):
    db_expense = get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.post("/", response_model=PydanticExpense)
def create_expense_route(expense: PydanticExpense, db: Session = Depends(set_rls_context), user: User = Depends(get_current_user)):
    return create_expense(db=db, expense=expense, user_id=user.id)

@router.put("/{expense_id}", response_model=PydanticExpense)
def update_expense_route(expense_id: UUID, expense: PydanticExpense, db: Session = Depends(set_rls_context)):
    db_expense = update_expense(db=db, expense_id=expense_id, expense=expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/{expense_id}")
def delete_expense_route(expense_id: UUID, db: Session = Depends(set_rls_context)):
    db_expense = delete_expense(db=db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

# Imports needed for the new endpoint
from fastapi import status
from pydantic import BaseModel
from typing import Union
from whatsapp_utils import send_reply

class ExpenseWhatsAppPayload(BaseModel):
    title: str
    amount: Union[float, int]
    category: str
    description: str
    date: str # Assuming date is passed as a string, e.g., "2025-12-03"
    phone: str # The recipient's WhatsApp number

@router.post("/send-whatsapp", status_code=status.HTTP_200_OK)
async def send_expense_to_whatsapp(payload: ExpenseWhatsAppPayload, user: User = Depends(get_current_user)):
    """
    Receives expense data and sends it as a WhatsApp message.
    This endpoint is protected and requires user authentication.
    """
    # 1. Construct the message body
    message_body = (
        "Expense Report\n"
        f"Title: {payload.title}\n"
        f"Amount: {payload.amount}\n"
        f"Category: {payload.category}\n"
        f"Description: {payload.description}\n"
        f"Date: {payload.date}"
    )

    # 2. Send the message using the utility function
    whatsapp_response = await send_reply(to=payload.phone, data=message_body)

    # 3. Handle the response from the WhatsApp API
    if not whatsapp_response or "messages" not in whatsapp_response:
        # The send_reply function might return None or an error structure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "message failed to send",
                "details": whatsapp_response or "An unknown error occurred while sending the message."
            }
        )

    # 4. Return a success response
    return {
        "status": "message sent",
        "details": whatsapp_response
    }
