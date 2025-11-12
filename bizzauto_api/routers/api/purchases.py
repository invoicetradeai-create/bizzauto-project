from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Purchase as PydanticPurchase
from crud import (
    get_purchase, get_purchases, create_purchase, update_purchase, delete_purchase
)

router = APIRouter()

@router.get("/", response_model=List[PydanticPurchase])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    purchases = get_purchases(db, skip=skip, limit=limit)
    return purchases

@router.get("/{purchase_id}", response_model=PydanticPurchase)
def read_purchase(purchase_id: UUID, db: Session = Depends(get_db)):
    db_purchase = get_purchase(db, purchase_id=purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return db_purchase

@router.post("/", response_model=PydanticPurchase)
def create_purchase_route(purchase: PydanticPurchase, db: Session = Depends(get_db)):
    return create_purchase(db=db, purchase=purchase)

@router.put("/{purchase_id}", response_model=PydanticPurchase)
def update_purchase_route(purchase_id: UUID, purchase: PydanticPurchase, db: Session = Depends(get_db)):
    db_purchase = update_purchase(db=db, purchase_id=purchase_id, purchase=purchase)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return db_purchase

@router.delete("/{purchase_id}")
def delete_purchase_route(purchase_id: UUID, db: Session = Depends(get_db)):
    db_purchase = delete_purchase(db=db, purchase_id=purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return {"message": "Purchase deleted successfully"}