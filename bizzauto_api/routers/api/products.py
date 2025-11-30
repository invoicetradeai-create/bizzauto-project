from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Product as PydanticProduct
from crud import (
    get_product, get_products, create_product, update_product, delete_product
)
from dependencies import set_rls_context, get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticProduct])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(set_rls_context)):
    products = get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=PydanticProduct)
def read_product(product_id: UUID, db: Session = Depends(set_rls_context)):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/", response_model=PydanticProduct)
def create_product_route(product: PydanticProduct, db: Session = Depends(set_rls_context), user: User = Depends(get_current_user)):
    return create_product(db=db, product=product, user_id=user.id)

@router.put("/{product_id}", response_model=PydanticProduct)
def update_product_route(product_id: UUID, product: PydanticProduct, db: Session = Depends(set_rls_context)):
    db_product = update_product(db=db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
def delete_product_route(product_id: UUID, db: Session = Depends(set_rls_context)):
    db_product = delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}