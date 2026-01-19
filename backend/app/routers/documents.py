from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models
from app.database.database import get_session

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get("/{space_id}", response_model=List[schemas.Document])
async def list_documents(space_id: str, session: AsyncSession = Depends(get_session)):

    return []


@router.delete("/{space_id}/{document_id}")
async def delete_document(
    space_id: str,
    document_id: str,
    session: AsyncSession = Depends(get_session),
    user: schemas.User = Depends()  # Required authentication
):
    return {"message": "Document deleted successfully"}


@router.post("/ingest/{space_id}", response_model=List[schemas.IngestResponse])
async def ingest_files(
    space_id: str,
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
    user: schemas.User = Depends()  # Required authentication
):
    responses = []

    return responses
