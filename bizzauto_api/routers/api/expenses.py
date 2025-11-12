from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Expense as PydanticExpense
from crud import (
    get_expense, get_expenses, create_expense, update_expense, delete_expense
)

router = APIRouter()

@router.get("/", response_model=List[PydanticExpense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = get_expenses(db, skip=skip, limit=limit)
    return expenses

@router.get("/{expense_id}", response_model=PydanticExpense)
def read_expense(expense_id: UUID, db: Session = Depends(get_db)):
    db_expense = get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.post("/", response_model=PydanticExpense)
def create_expense_route(expense: PydanticExpense, db: Session = Depends(get_db)):
    return create_expense(db=db, expense=expense)

@router.put("/{expense_id}", response_model=PydanticExpense)
def update_expense_route(expense_id: UUID, expense: PydanticExpense, db: Session = Depends(get_db)):
    db_expense = update_expense(db=db, expense_id=expense_id, expense=expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/{expense_id}")
def delete_expense_route(expense_id: UUID, db: Session = Depends(get_db)):
    db_expense = delete_expense(db=db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}