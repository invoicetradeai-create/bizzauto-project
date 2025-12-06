from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud
from dependencies import get_current_user, set_rls_context
from sql_models import User

router = APIRouter()

@router.get("/inventory/stock-summary")
def get_stock_summary(db: Session = Depends(set_rls_context), user: User = Depends(get_current_user)):
    summary = crud.get_stock_summary(db, user_id=user.id)
    return [{"name": name, "stock_quantity": stock_quantity} for name, stock_quantity in summary]
