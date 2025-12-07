from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import User as PydanticUser
from crud import (
    get_user, get_users, create_user, update_user, delete_user
)
import dependencies as deps
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticUser])
def read_users():
    print("DEBUG: read_users endpoint hit!")
    dummy_user = {
        "id": "00000000-0000-0000-0000-000000000001",
        "company_id": "00000000-0000-0000-0000-000000000001",
        "full_name": "Test User",
        "email": "test@example.com",
        "role": "user",
        "business_name": "Test Business",
        "location": "Test Location",
        "contact_number": "1234567890",
        "status": "active",
        "created_at": "2023-01-01T00:00:00Z"
    }
    return [dummy_user]

@router.get("/me", response_model=PydanticUser)
def read_users_me(current_user: PydanticUser = Depends(deps.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=PydanticUser)
def read_user(user_id: UUID, db: Session = Depends(deps.set_rls_context)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/", response_model=PydanticUser)
def create_user_route(user: PydanticUser, db: Session = Depends(deps.set_rls_context)):
    print("--- Creating User ---")
    print(user.model_dump_json(indent=2))
    print("---------------------")
    return create_user(db=db, user=user)

@router.put("/{user_id}", response_model=PydanticUser)
def update_user_route(user_id: UUID, user: PydanticUser, db: Session = Depends(deps.set_rls_context)):
    db_user = update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def delete_user_route(user_id: UUID, db: Session = Depends(deps.set_rls_context)):
    db_user = delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}