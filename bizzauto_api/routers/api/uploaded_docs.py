from fastapi import APIRouter, HTTPException, Body
from db import supabase
from models import UploadedDoc
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[UploadedDoc])
async def get_all_uploaded_docs():
    try:
        response = supabase.table('uploaded_docs').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=UploadedDoc)
async def get_uploaded_doc_by_id(id: UUID):
    try:
        response = supabase.table('uploaded_docs').select('*').eq('id', str(id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Uploaded doc not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=UploadedDoc)
async def create_uploaded_doc(uploaded_doc: UploadedDoc):
    try:
        response = supabase.table('uploaded_docs').insert(uploaded_doc.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=UploadedDoc)
async def update_uploaded_doc(id: UUID, uploaded_doc: UploadedDoc):
    try:
        response = supabase.table('uploaded_docs').update(uploaded_doc.dict(exclude_unset=True)).eq('id', str(id)).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def delete_uploaded_doc(id: UUID):
    try:
        response = supabase.table('uploaded_docs').delete().eq('id', str(id)).execute()
        return {"message": "Uploaded doc deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
