from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Invoice as PydanticInvoice
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
def create_invoice_route(invoice: PydanticInvoice, db: Session = Depends(get_db)):
    # TEMPORARY FIX: Inject a default company_id if not provided by the frontend
    # This should be handled by getting the user's company from their session/token
    if not hasattr(invoice, 'company_id') or not invoice.company_id:
        invoice.company_id = UUID("94bb2f7b-5ce9-4f9b-b097-5ef45e75c2fa") # Hardcoded default
    return create_invoice(db=db, invoice=invoice)

@router.put("/{invoice_id}", response_model=PydanticInvoice)
def update_invoice_route(invoice_id: UUID, invoice: PydanticInvoice, db: Session = Depends(get_db)):
    # TEMPORARY FIX: Inject a default company_id if not provided
    if not hasattr(invoice, 'company_id') or not invoice.company_id:
        invoice.company_id = UUID("94bb2f7b-5ce9-4f9b-b097-5ef45e75c2fa") # Hardcoded default
    db_invoice = update_invoice(db=db, invoice_id=invoice_id, invoice=invoice)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.delete("/{invoice_id}")
def delete_invoice_route(invoice_id: UUID, db: Session = Depends(get_db)):
    db_invoice = delete_invoice(db=db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}