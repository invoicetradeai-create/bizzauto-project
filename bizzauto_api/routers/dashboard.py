from fastapi import APIRouter
from db import supabase

router = APIRouter()

@router.get("/analytics")
async def get_analytics():
    return {"message": "Analytics data"}

@router.get("/crm")
async def get_crm():
    return {"message": "CRM data"}

@router.get("/dashboard")
async def get_dashboard():
    response = supabase.table('dashboard_items').select('*').execute()
    return response.data

@router.post("/dashboard/add")
async def add_dashboard_item(item: dict):
    response = supabase.table('dashboard_items').insert(item).execute()
    return response.data

@router.get("/inventory")
async def get_inventory():
    return {"message": "Inventory data"}

@router.get("/invoices")
async def get_invoices():
    return {"message": "Invoices data"}

@router.get("/settings")
async def get_settings():
    return {"message": "Settings data"}

@router.get("/whatsapp")
async def get_whatsapp():
    return {"message": "WhatsApp data"}
