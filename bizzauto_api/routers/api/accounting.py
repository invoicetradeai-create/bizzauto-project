from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import crud
import models
import sql_models
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sales_summary", response_model=list[models.Invoice])
def get_sales_summary(db: Session = Depends(get_db)):
    """
    Get a summary of sales.
    """
    return db.query(sql_models.Invoice).all()

@router.get("/expense_report", response_model=list[models.ExpenseReport])
def get_expense_report(db: Session = Depends(get_db)):
    """
    Get a summary of expenses.
    """
    results = db.query(
        sql_models.Expense.category, 
        func.sum(sql_models.Expense.amount).label("sum")
    ).group_by(sql_models.Expense.category).all()
    return [models.ExpenseReport(category=category, sum=sum) for category, sum in results]

@router.get("/stock_report", response_model=list[models.Product])
def get_stock_report(db: Session = Depends(get_db)):
    """
    Get a summary of stock.
    """
    return db.query(sql_models.Product).all()
