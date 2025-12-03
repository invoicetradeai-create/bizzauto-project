from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import crud
import models
import sql_models
from database import SessionLocal
from dependencies import get_current_user
from sql_models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sales_summary", response_model=list[models.Invoice])
def get_sales_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get a summary of sales for the current user.
    """
    return db.query(sql_models.Invoice).filter(sql_models.Invoice.user_id == user.id).all()

@router.get("/expense_report", response_model=list[models.ExpenseReport])
def get_expense_report(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get a summary of expenses for the current user.
    """
    results = db.query(
        sql_models.Expense.category, 
        func.sum(sql_models.Expense.amount).label("sum")
    ).filter(sql_models.Expense.user_id == user.id).group_by(sql_models.Expense.category).all()
    return [models.ExpenseReport(category=category, sum=sum) for category, sum in results]

@router.get("/stock_report", response_model=list[models.Product])
def get_stock_report(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get a summary of stock for the current user.
    """
    return db.query(sql_models.Product).filter(sql_models.Product.user_id == user.id).all()
