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

@router.post("/scheduled-whatsapp-messages", response_model=PydanticScheduledWhatsappMessage, tags=["Scheduled WhatsApp Messages"])
def create_scheduled_message(
    scheduled_message_data: ScheduledWhatsappMessageCreate, 
    db: Session = Depends(set_rls_context),
    user: User = Depends(get_current_user)
):
    company_id = user.company_id
    
    scheduled_message = PydanticScheduledWhatsappMessage(
        **scheduled_message_data.model_dump(),
        company_id=company_id
    )
    
    return crud.create_scheduled_whatsapp_message(db=db, scheduled_message=scheduled_message, user_id=user.id)

@router.get("/scheduled-whatsapp-messages", response_model=List[PydanticScheduledWhatsappMessage], tags=["Scheduled WhatsApp Messages"])
def read_scheduled_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(set_rls_context)
):
    messages = crud.get_scheduled_whatsapp_messages(db, skip=skip, limit=limit)
    return messages
