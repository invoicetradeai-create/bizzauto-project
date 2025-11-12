from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import WhatsappLog as PydanticWhatsappLog
from crud import (
    get_whatsapp_log, get_whatsapp_logs, create_whatsapp_log, update_whatsapp_log, delete_whatsapp_log
)

router = APIRouter()

@router.get("/", response_model=List[PydanticWhatsappLog])
def read_whatsapp_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    whatsapp_logs = get_whatsapp_logs(db, skip=skip, limit=limit)
    return whatsapp_logs

@router.get("/{whatsapp_log_id}", response_model=PydanticWhatsappLog)
def read_whatsapp_log(whatsapp_log_id: UUID, db: Session = Depends(get_db)):
    db_whatsapp_log = get_whatsapp_log(db, whatsapp_log_id=whatsapp_log_id)
    if db_whatsapp_log is None:
        raise HTTPException(status_code=404, detail="Whatsapp log not found")
    return db_whatsapp_log

@router.post("/", response_model=PydanticWhatsappLog)
def create_whatsapp_log_route(whatsapp_log: PydanticWhatsappLog, db: Session = Depends(get_db)):
    return create_whatsapp_log(db=db, whatsapp_log=whatsapp_log)

@router.put("/{whatsapp_log_id}", response_model=PydanticWhatsappLog)
def update_whatsapp_log_route(whatsapp_log_id: UUID, whatsapp_log: PydanticWhatsappLog, db: Session = Depends(get_db)):
    db_whatsapp_log = update_whatsapp_log(db=db, whatsapp_log_id=whatsapp_log_id, whatsapp_log=whatsapp_log)
    if db_whatsapp_log is None:
        raise HTTPException(status_code=404, detail="Whatsapp log not found")
    return db_whatsapp_log

@router.delete("/{whatsapp_log_id}")
def delete_whatsapp_log_route(whatsapp_log_id: UUID, db: Session = Depends(get_db)):
    db_whatsapp_log = delete_whatsapp_log(db=db, whatsapp_log_id=whatsapp_log_id)
    if db_whatsapp_log is None:
        raise HTTPException(status_code=404, detail="Whatsapp log not found")
    return {"message": "Whatsapp log deleted successfully"}