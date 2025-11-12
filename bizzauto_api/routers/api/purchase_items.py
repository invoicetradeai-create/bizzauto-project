from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import PurchaseItem as PydanticPurchaseItem
from crud import (
    get_purchase_item, get_purchase_items, create_purchase_item, update_purchase_item, delete_purchase_item
)

router = APIRouter()

@router.get("/", response_model=List[PydanticPurchaseItem])
def read_purchase_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    purchase_items = get_purchase_items(db, skip=skip, limit=limit)
    return purchase_items

@router.get("/{purchase_item_id}", response_model=PydanticPurchaseItem)
def read_purchase_item(purchase_item_id: UUID, db: Session = Depends(get_db)):
    db_purchase_item = get_purchase_item(db, purchase_item_id=purchase_item_id)
    if db_purchase_item is None:
        raise HTTPException(status_code=404, detail="Purchase item not found")
    return db_purchase_item

@router.post("/", response_model=PydanticPurchaseItem)
def create_purchase_item_route(purchase_item: PydanticPurchaseItem, db: Session = Depends(get_db)):
    return create_purchase_item(db=db, purchase_item=purchase_item)

@router.put("/{purchase_item_id}", response_model=PydanticPurchaseItem)
def update_purchase_item_route(purchase_item_id: UUID, purchase_item: PydanticPurchaseItem, db: Session = Depends(get_db)):
    db_purchase_item = update_purchase_item(db=db, purchase_item_id=purchase_item_id, purchase_item=purchase_item)
    if db_purchase_item is None:
        raise HTTPException(status_code=404, detail="Purchase item not found")
    return db_purchase_item

@router.delete("/{purchase_item_id}")
def delete_purchase_item_route(purchase_item_id: UUID, db: Session = Depends(get_db)):
    db_purchase_item = delete_purchase_item(db=db, purchase_item_id=purchase_item_id)
    if db_purchase_item is None:
        raise HTTPException(status_code=404, detail="Purchase item not found")
    return {"message": "Purchase item deleted successfully"}