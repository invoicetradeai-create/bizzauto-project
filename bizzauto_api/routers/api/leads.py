from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Lead
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Lead])
async def get_all_leads():
    try:
        response = supabase.table('leads').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Lead)
async def get_lead_by_id(id: UUID):
    try:
        response = supabase.table('leads').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Lead)
async def create_lead(lead: Lead):
    try:
        response = supabase.table('leads').insert(lead.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Lead)
async def update_lead(id: UUID, lead: Lead):
    try:
        response = supabase.table('leads').update(lead.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_lead(id: UUID):
    try:
        response = supabase.table('leads').delete().eq('id', str(id)).execute()
        return {"message": "Lead deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
