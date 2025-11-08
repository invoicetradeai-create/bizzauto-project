from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Client
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Client])
async def get_all_clients():
    try:
        response = supabase.table('clients').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Client)
async def get_client_by_id(id: UUID):
    try:
        response = supabase.table('clients').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Client not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Client)
async def create_client(client: Client):
    try:
        response = supabase.table('clients').insert(client.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Client)
async def update_client(id: UUID, client: Client):
    try:
        response = supabase.table('clients').update(client.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_client(id: UUID):
    try:
        response = supabase.table('clients').delete().eq('id', str(id)).execute()
        return {"message": "Client deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
