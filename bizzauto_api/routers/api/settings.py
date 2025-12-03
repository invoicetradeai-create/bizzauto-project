from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Setting as PydanticSetting
from crud import (
    get_setting, get_settings, create_setting, update_setting, delete_setting
)
from dependencies import get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticSetting])
def read_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    settings = get_settings(db, user_id=user.id, skip=skip, limit=limit)
    return settings

@router.get("/{setting_id}", response_model=PydanticSetting)
def read_setting(setting_id: UUID, db: Session = Depends(get_db)):
    db_setting = get_setting(db, setting_id=setting_id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_setting

@router.post("/", response_model=PydanticSetting)
def create_setting_route(setting: PydanticSetting, db: Session = Depends(get_db)):
    return create_setting(db=db, setting=setting)

@router.put("/{setting_id}", response_model=PydanticSetting)
def update_setting_route(setting_id: UUID, setting: PydanticSetting, db: Session = Depends(get_db)):
    db_setting = update_setting(db=db, setting_id=setting_id, setting=setting)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_setting

@router.delete("/{setting_id}")
def delete_setting_route(setting_id: UUID, db: Session = Depends(get_db)):
    db_setting = delete_setting(db=db, setting_id=setting_id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}