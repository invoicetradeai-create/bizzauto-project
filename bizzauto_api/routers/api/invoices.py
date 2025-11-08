from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Invoice
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Invoice])
async def get_all_invoices():
    try:
        response = supabase.table('invoices').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Invoice)
async def get_invoice_by_id(id: UUID):
    try:
        response = supabase.table('invoices').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Invoice)
async def create_invoice(invoice: Invoice):
    try:
        response = supabase.table('invoices').insert(invoice.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Invoice)
async def update_invoice(id: UUID, invoice: Invoice):
    try:
        response = supabase.table('invoices').update(invoice.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_invoice(id: UUID):
    try:
        response = supabase.table('invoices').delete().eq('id', str(id)).execute()
        return {"message": "Invoice deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
