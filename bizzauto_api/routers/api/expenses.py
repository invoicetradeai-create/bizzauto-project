from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import Expense
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Expense])
async def get_all_expenses():
    try:
        response = supabase.table('expenses').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Expense)
async def get_expense_by_id(id: UUID):
    try:
        response = supabase.table('expenses').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Expense not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Expense)
async def create_expense(expense: Expense):
    try:
        response = supabase.table('expenses').insert(expense.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=Expense)
async def update_expense(id: UUID, expense: Expense):
    try:
        response = supabase.table('expenses').update(expense.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_expense(id: UUID):
    try:
        response = supabase.table('expenses').delete().eq('id', str(id)).execute()
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
