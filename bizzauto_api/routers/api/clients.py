
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Client as PydanticClient
from crud import (
    get_client, get_clients, create_client, update_client, delete_client
)
from dependencies import set_rls_context, get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticClient])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(set_rls_context)):
    clients = get_clients(db, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=PydanticClient)
def read_client(client_id: UUID, db: Session = Depends(set_rls_context)):
    db_client = get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.post("/", response_model=PydanticClient)
def create_client_route(client: PydanticClient, db: Session = Depends(set_rls_context), user: User = Depends(get_current_user)):
    return create_client(db=db, client=client, user_id=user.id)

@router.put("/{client_id}", response_model=PydanticClient)
def update_client_route(client_id: UUID, client: PydanticClient, db: Session = Depends(set_rls_context)):
    db_client = update_client(db=db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.delete("/{client_id}")
def delete_client_route(client_id: UUID, db: Session = Depends(set_rls_context)):
    db_client = delete_client(db=db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}
