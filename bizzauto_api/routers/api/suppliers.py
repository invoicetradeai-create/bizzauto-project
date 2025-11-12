from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Supplier as PydanticSupplier
from crud import (
    get_supplier, get_suppliers, create_supplier, update_supplier, delete_supplier
)

router = APIRouter()

@router.get("/", response_model=List[PydanticSupplier])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    suppliers = get_suppliers(db, skip=skip, limit=limit)
    return suppliers

@router.get("/{supplier_id}", response_model=PydanticSupplier)
def read_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    db_supplier = get_supplier(db, supplier_id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.post("/", response_model=PydanticSupplier)
def create_supplier_route(supplier: PydanticSupplier, db: Session = Depends(get_db)):
    return create_supplier(db=db, supplier=supplier)

@router.put("/{supplier_id}", response_model=PydanticSupplier)
def update_supplier_route(supplier_id: UUID, supplier: PydanticSupplier, db: Session = Depends(get_db)):
    db_supplier = update_supplier(db=db, supplier_id=supplier_id, supplier=supplier)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.delete("/{supplier_id}")
def delete_supplier_route(supplier_id: UUID, db: Session = Depends(get_db)):
    db_supplier = delete_supplier(db=db, supplier_id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}