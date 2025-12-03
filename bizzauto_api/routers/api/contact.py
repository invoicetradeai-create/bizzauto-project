from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import sql_models
from pydantic import BaseModel, EmailStr

router = APIRouter()

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_contact_message(request: ContactRequest, db: Session = Depends(get_db)):
    new_message = sql_models.ContactMessage(
        name=request.name,
        email=request.email,
        phone=request.phone,
        subject=request.subject,
        message=request.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # TODO: Send notification to admin (email/whatsapp)
    # For now, we just log it or assume another service picks it up
    
    return {"message": "Message sent successfully", "id": str(new_message.id)}
