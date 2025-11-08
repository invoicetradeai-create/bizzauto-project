from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import InvoiceItem
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[InvoiceItem])
async def get_all_invoice_items():
    try:
        response = supabase.table('invoice_items').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=InvoiceItem)
async def get_invoice_item_by_id(id: UUID):
    try:
        response = supabase.table('invoice_items').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice item not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=InvoiceItem)
async def create_invoice_item(invoice_item: InvoiceItem):
    try:
        response = supabase.table('invoice_items').insert(invoice_item.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=InvoiceItem)
async def update_invoice_item(id: UUID, invoice_item: InvoiceItem):
    try:
        response = supabase.table('invoice_items').update(invoice_item.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_invoice_item(id: UUID):
    try:
        response = supabase.table('invoice_items').delete().eq('id', str(id)).execute()
        return {"message": "Invoice item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
