from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Invoice as PydanticInvoice, InvoiceCreate
from crud import (
    get_invoice, get_invoices, create_invoice, update_invoice, delete_invoice
)

router = APIRouter()

@router.get("/", response_model=List[PydanticInvoice])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    invoices = get_invoices(db, skip=skip, limit=limit)
    return invoices

@router.get("/{invoice_id}", response_model=PydanticInvoice)
def read_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    db_invoice = get_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.post("/", response_model=PydanticInvoice)
def create_invoice_route(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    # TEMPORARY FIX: Inject a default company_id
    company_id = UUID("94bb2f7b-5ce9-4f9b-b097-5ef45e75c2fa")
    return create_invoice(db=db, invoice=invoice, company_id=company_id)

@router.put("/{invoice_id}", response_model=PydanticInvoice)
def update_invoice_route(invoice_id: UUID, invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = update_invoice(db=db, invoice_id=invoice_id, invoice_data=invoice)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.delete("/{invoice_id}")
def delete_invoice_route(invoice_id: UUID, db: Session = Depends(get_db)):
    db_invoice = delete_invoice(db=db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}