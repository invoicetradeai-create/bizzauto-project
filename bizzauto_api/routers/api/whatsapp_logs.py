from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import WhatsappLog
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[WhatsappLog])
async def get_all_whatsapp_logs():
    try:
        response = supabase.table('whatsapp_logs').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=WhatsappLog)
async def get_whatsapp_log_by_id(id: UUID):
    try:
        response = supabase.table('whatsapp_logs').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Whatsapp log not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=WhatsappLog)
async def create_whatsapp_log(whatsapp_log: WhatsappLog):
    try:
        response = supabase.table('whatsapp_logs').insert(whatsapp_log.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=WhatsappLog)
async def update_whatsapp_log(id: UUID, whatsapp_log: WhatsappLog):
    try:
        response = supabase.table('whatsapp_logs').update(whatsapp_log.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_whatsapp_log(id: UUID):
    try:
        response = supabase.table('whatsapp_logs').delete().eq('id', str(id)).execute()
        return {"message": "Whatsapp log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
