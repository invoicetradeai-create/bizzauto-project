from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
import crud
from models import ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage, ScheduledWhatsappMessageCreate, Company as PydanticCompany

router = APIRouter()

@router.post("/scheduled-whatsapp-messages", response_model=PydanticScheduledWhatsappMessage, tags=["Scheduled WhatsApp Messages"])
def create_scheduled_message(
    scheduled_message_data: ScheduledWhatsappMessageCreate, 
    db: Session = Depends(get_db)
):
    # In a real app, you'd get the company_id from the authenticated user
    # For now, we'll fetch the first company as a placeholder
    companies = crud.get_companies(db, skip=0, limit=1)
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found to associate the message with.")
    
    company_id = companies[0].id
    
    scheduled_message = PydanticScheduledWhatsappMessage(
        **scheduled_message_data.model_dump(),
        company_id=company_id
    )
    
    return crud.create_scheduled_whatsapp_message(db=db, scheduled_message=scheduled_message)

@router.get("/scheduled-whatsapp-messages", response_model=List[PydanticScheduledWhatsappMessage], tags=["Scheduled WhatsApp Messages"])
def read_scheduled_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    messages = crud.get_scheduled_whatsapp_messages(db, skip=skip, limit=limit)
    return messages
