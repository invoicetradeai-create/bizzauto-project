from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Purchase
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Purchase])
async def get_all_purchases():
    try:
        response = supabase.table('purchases').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Purchase)
async def get_purchase_by_id(id: UUID):
    try:
        response = supabase.table('purchases').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Purchase not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Purchase)
async def create_purchase(purchase: Purchase):
    try:
        response = supabase.table('purchases').insert(purchase.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Purchase)
async def update_purchase(id: UUID, purchase: Purchase):
    try:
        response = supabase.table('purchases').update(purchase.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_purchase(id: UUID):
    try:
        response = supabase.table('purchases').delete().eq('id', str(id)).execute()
        return {"message": "Purchase deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
