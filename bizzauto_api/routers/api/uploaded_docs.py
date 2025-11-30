from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import UploadedDoc as PydanticUploadedDoc
from crud import (
    get_uploaded_doc, get_uploaded_docs, create_uploaded_doc, update_uploaded_doc, delete_uploaded_doc
)
from dependencies import set_rls_context, get_current_user
from sql_models import User

router = APIRouter()

@router.get("/", response_model=List[PydanticUploadedDoc])
def read_uploaded_docs(skip: int = 0, limit: int = 100, db: Session = Depends(set_rls_context)):
    uploaded_docs = get_uploaded_docs(db, skip=skip, limit=limit)
    return uploaded_docs

@router.get("/{uploaded_doc_id}", response_model=PydanticUploadedDoc)
def read_uploaded_doc(uploaded_doc_id: UUID, db: Session = Depends(set_rls_context)):
    db_uploaded_doc = get_uploaded_doc(db, uploaded_doc_id=uploaded_doc_id)
    if db_uploaded_doc is None:
        raise HTTPException(status_code=404, detail="Uploaded doc not found")
    return db_uploaded_doc

@router.post("/", response_model=PydanticUploadedDoc)
def create_uploaded_doc_route(uploaded_doc: PydanticUploadedDoc, db: Session = Depends(set_rls_context), user: User = Depends(get_current_user)):
    return create_uploaded_doc(db=db, uploaded_doc=uploaded_doc, user_id=user.id)

@router.put("/{uploaded_doc_id}", response_model=PydanticUploadedDoc)
def update_uploaded_doc_route(uploaded_doc_id: UUID, uploaded_doc: PydanticUploadedDoc, db: Session = Depends(set_rls_context)):
    db_uploaded_doc = update_uploaded_doc(db=db, uploaded_doc_id=uploaded_doc_id, uploaded_doc=uploaded_doc)
    if db_uploaded_doc is None:
        raise HTTPException(status_code=404, detail="Uploaded doc not found")
    return db_uploaded_doc

@router.delete("/{uploaded_doc_id}")
def delete_uploaded_doc_route(uploaded_doc_id: UUID, db: Session = Depends(set_rls_context)):
    db_uploaded_doc = delete_uploaded_doc(db=db, uploaded_doc_id=uploaded_doc_id)
    if db_uploaded_doc is None:
        raise HTTPException(status_code=404, detail="Uploaded doc not found")
    return {"message": "Uploaded doc deleted successfully"}