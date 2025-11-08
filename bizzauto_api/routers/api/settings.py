from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Setting
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Setting])
async def get_all_settings():
    try:
        response = supabase.table('settings').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Setting)
async def get_setting_by_id(id: UUID):
    try:
        response = supabase.table('settings').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Setting not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Setting)
async def create_setting(setting: Setting):
    try:
        response = supabase.table('settings').insert(setting.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Setting)
async def update_setting(id: UUID, setting: Setting):
    try:
        response = supabase.table('settings').update(setting.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_setting(id: UUID):
    try:
        response = supabase.table('settings').delete().eq('id', str(id)).execute()
        return {"message": "Setting deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
