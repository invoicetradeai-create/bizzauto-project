from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from sql_models import User
from uuid import UUID

def get_current_user(x_user_id: str = Header(None), db: Session = Depends(get_db)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")
    
    try:
        user_uuid = UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
