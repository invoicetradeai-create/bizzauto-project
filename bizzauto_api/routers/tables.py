from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import (
    Company, Client, User, Supplier, Product, Invoice, InvoiceItem, 
    Purchase, PurchaseItem, Expense, Lead, WhatsappLog, UploadedDoc, Setting
)
from typing import Union

router = APIRouter()

models = {
    "companies": Company,
    "clients": Client,
    "users": User,
    "suppliers": Supplier,
    "products": Product,
    "invoices": Invoice,
    "invoice_items": InvoiceItem,
    "purchases": Purchase,
    "purchase_items": PurchaseItem,
    "expenses": Expense,
    "leads": Lead,
    "whatsapp_logs": WhatsappLog,
    "uploaded_docs": UploadedDoc,
    "settings": Setting,
}

@router.get("/")
async def get_all_tables():
    try:
        response = supabase.rpc('get_all_tables', {}).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{table_name}")
async def get_all_records(table_name: str):
    try:
        response = supabase.table(table_name).select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{table_name}/{id}")
async def get_record_by_id(table_name: str, id: str):
    try:
        response = supabase.table(table_name).select('*').eq('id', id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Record not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{table_name}")
async def create_record(table_name: str, record: Union[Company, Client, User, Supplier, Product, Invoice, InvoiceItem, Purchase, PurchaseItem, Expense, Lead, WhatsappLog, UploadedDoc, Setting, dict] = Body(...)):
    try:
        model = models.get(table_name)
        if model and not isinstance(record, dict):
            record_data = record.dict()
        else:
            record_data = record

        response = supabase.table(table_name).insert(record_data).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{table_name}/{id}")
async def update_record(table_name: str, id: str, record: Union[Company, Client, User, Supplier, Product, Invoice, InvoiceItem, Purchase, PurchaseItem, Expense, Lead, WhatsappLog, UploadedDoc, Setting, dict] = Body(...)):
    try:
        model = models.get(table_name)
        if model and not isinstance(record, dict):
            record_data = record.dict(exclude_unset=True)
        else:
            record_data = record

        response = supabase.table(table_name).update(record_data).eq('id', id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{table_name}/{id}")
async def delete_record(table_name: str, id: str):
    try:
        response = supabase.table(table_name).delete().eq('id', id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
