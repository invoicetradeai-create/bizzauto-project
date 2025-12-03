from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Company as PydanticCompany
from crud import (
    get_company, get_companies, create_company, update_company, delete_company
)

router = APIRouter()

@router.get("/", response_model=List[PydanticCompany])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = get_companies(db, skip=skip, limit=limit)
    return companies

@router.get("/{company_id}", response_model=PydanticCompany)
def read_company(company_id: UUID, db: Session = Depends(get_db)):
    db_company = get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.post("/", response_model=PydanticCompany)
def create_company_route(company: PydanticCompany, db: Session = Depends(get_db)):
    return create_company(db=db, company=company)

@router.put("/{company_id}", response_model=PydanticCompany)
def update_company_route(company_id: UUID, company: PydanticCompany, db: Session = Depends(get_db)):
    db_company = update_company(db=db, company_id=company_id, company=company)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.delete("/{company_id}")
def delete_company_route(company_id: UUID, db: Session = Depends(get_db)):
    db_company = delete_company(db=db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}