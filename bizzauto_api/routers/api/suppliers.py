from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Supplier
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Supplier])
async def get_all_suppliers():
    try:
        response = supabase.table('suppliers').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Supplier)
async def get_supplier_by_id(id: UUID):
    try:
        response = supabase.table('suppliers').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Supplier)
async def create_supplier(supplier: Supplier):
    try:
        response = supabase.table('suppliers').insert(supplier.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Supplier)
async def update_supplier(id: UUID, supplier: Supplier):
    try:
        response = supabase.table('suppliers').update(supplier.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_supplier(id: UUID):
    try:
        response = supabase.table('suppliers').delete().eq('id', str(id)).execute()
        return {"message": "Supplier deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
