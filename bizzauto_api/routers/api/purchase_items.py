from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import PurchaseItem
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[PurchaseItem])
async def get_all_purchase_items():
    try:
        response = supabase.table('purchase_items').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=PurchaseItem)
async def get_purchase_item_by_id(id: UUID):
    try:
        response = supabase.table('purchase_items').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Purchase item not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=PurchaseItem)
async def create_purchase_item(purchase_item: PurchaseItem):
    try:
        response = supabase.table('purchase_items').insert(purchase_item.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=PurchaseItem)
async def update_purchase_item(id: UUID, purchase_item: PurchaseItem):
    try:
        response = supabase.table('purchase_items').update(purchase_item.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_purchase_item(id: UUID):
    try:
        response = supabase.table('purchase_items').delete().eq('id', str(id)).execute()
        return {"message": "Purchase item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
