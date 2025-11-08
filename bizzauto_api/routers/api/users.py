from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import User
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_all_users():
    try:
        response = supabase.table('users').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=User)
async def get_user_by_id(id: UUID):
    try:
        response = supabase.table('users').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=User)
async def create_user(user: User):
    try:
        response = supabase.table('users').insert(user.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=User)
async def update_user(id: UUID, user: User):
    try:
        response = supabase.table('users').update(user.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_user(id: UUID):
    try:
        response = supabase.table('users').delete().eq('id', str(id)).execute()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
