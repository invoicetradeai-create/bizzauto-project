from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Company
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Company])
async def get_all_companies():
    try:
        response = supabase.table('companies').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Company)
async def get_company_by_id(id: UUID):
    try:
        response = supabase.table('companies').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Company not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Company)
async def create_company(company: Company):
    try:
        response = supabase.table('companies').insert(company.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Company)
async def update_company(id: UUID, company: Company):
    try:
        response = supabase.table('companies').update(company.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_company(id: UUID):
    try:
        response = supabase.table('companies').delete().eq('id', str(id)).execute()
        return {"message": "Company deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
