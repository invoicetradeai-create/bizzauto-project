from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Lead as PydanticLead
from crud import (
    get_lead, get_leads, create_lead, update_lead, delete_lead
)

router = APIRouter()

@router.get("/", response_model=List[PydanticLead])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = get_leads(db, skip=skip, limit=limit)
    return leads

@router.get("/{lead_id}", response_model=PydanticLead)
def read_lead(lead_id: UUID, db: Session = Depends(get_db)):
    db_lead = get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.post("/", response_model=PydanticLead)
def create_lead_route(lead: PydanticLead, db: Session = Depends(get_db)):
    return create_lead(db=db, lead=lead)

@router.put("/{lead_id}", response_model=PydanticLead)
def update_lead_route(lead_id: UUID, lead: PydanticLead, db: Session = Depends(get_db)):
    db_lead = update_lead(db=db, lead_id=lead_id, lead=lead)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.delete("/{lead_id}")
def delete_lead_route(lead_id: UUID, db: Session = Depends(get_db)):
    db_lead = delete_lead(db=db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}