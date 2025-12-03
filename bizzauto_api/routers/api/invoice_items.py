from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import InvoiceItem as PydanticInvoiceItem
from crud import (
    get_invoice_item, get_invoice_items, create_invoice_item, update_invoice_item, delete_invoice_item
)
from dependencies import get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticInvoiceItem])
def read_invoice_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice_items = get_invoice_items(db, user_id=user.id, skip=skip, limit=limit)
    return invoice_items

@router.get("/{invoice_item_id}", response_model=PydanticInvoiceItem)
def read_invoice_item(invoice_item_id: UUID, db: Session = Depends(get_db)):
    db_invoice_item = get_invoice_item(db, invoice_item_id=invoice_item_id)
    if db_invoice_item is None:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return db_invoice_item

@router.post("/", response_model=PydanticInvoiceItem)
def create_invoice_item_route(invoice_item: PydanticInvoiceItem, db: Session = Depends(get_db)):
    return create_invoice_item(db=db, invoice_item=invoice_item)

@router.put("/{invoice_item_id}", response_model=PydanticInvoiceItem)
def update_invoice_item_route(invoice_item_id: UUID, invoice_item: PydanticInvoiceItem, db: Session = Depends(get_db)):
    db_invoice_item = update_invoice_item(db=db, invoice_item_id=invoice_item_id, invoice_item=invoice_item)
    if db_invoice_item is None:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return db_invoice_item

@router.delete("/{invoice_item_id}")
def delete_invoice_item_route(invoice_item_id: UUID, db: Session = Depends(get_db)):
    db_invoice_item = delete_invoice_item(db=db, invoice_item_id=invoice_item_id)
    if db_invoice_item is None:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return {"message": "Invoice item deleted successfully"}