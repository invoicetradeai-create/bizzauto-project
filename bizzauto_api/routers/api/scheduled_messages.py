from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
import crud
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage, ScheduledWhatsappMessageCreate, Company as PydanticCompany
from dependencies import set_rls_context, get_current_user
from sql_models import User

router = APIRouter()

@router.post("/scheduled-whatsapp-messages", tags=["Scheduled WhatsApp Messages"])
def create_scheduled_message(
    scheduled_message_data: ScheduledWhatsappMessageCreate, 
    db: Session = Depends(set_rls_context),
    user: User = Depends(get_current_user)
):
    company_id = user.company_id
    
    print(f"Received request to schedule message: {scheduled_message_data}")
    
    scheduled_message = PydanticScheduledWhatsappMessage(
        **scheduled_message_data.model_dump(),
        company_id=company_id
    )
    
    print(f"Prepared Pydantic model: {scheduled_message}", flush=True)
    
    result = crud.create_scheduled_whatsapp_message(db=db, scheduled_message=scheduled_message, user_id=user.id)
    print(f"CRUD Result: {result.__dict__}", flush=True)
    
    return {"status": "success", "message": "Message scheduled successfully"}

@router.get("/scheduled-whatsapp-messages", response_model=List[PydanticScheduledWhatsappMessage], tags=["Scheduled WhatsApp Messages"])
def read_scheduled_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    messages = crud.get_scheduled_whatsapp_messages(db, user_id=user.id, skip=skip, limit=limit)
    return messages
