from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()

@router.get("/inventory/stock-summary")
def get_stock_summary(db: Session = Depends(get_db)):
    summary = crud.get_stock_summary(db)
    return [{"name": name, "stock_quantity": stock_quantity} for name, stock_quantity in summary]
