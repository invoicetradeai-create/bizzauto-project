from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Product
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_all_products():
    try:
        response = supabase.table('products').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Product)
async def get_product_by_id(id: UUID):
    try:
        response = supabase.table('products').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Product)
async def create_product(product: Product):
    try:
        response = supabase.table('products').insert(product.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Product)
async def update_product(id: UUID, product: Product):
    try:
        response = supabase.table('products').update(product.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_product(id: UUID):
    try:
        response = supabase.table('products').delete().eq('id', str(id)).execute()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
