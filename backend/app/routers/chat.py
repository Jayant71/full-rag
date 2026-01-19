from re import A
import uuid
from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models import Space

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("/chat/{space_id}", response_model=schemas.ChatResponse)
async def chat(
    space_id: str,
    request: schemas.ChatRequest,
    session: AsyncSession = Depends(get_session),
    user: schemas.User = Depends()
):
    if not user:
        raise HTTPException(
            status_code=401, detail="Authentication required. Please sign in.")

    space = session.get(Space, uuid.UUID(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    try:
        chat_response = schemas.ChatResponse(
            answer="This is a placeholder response.",
            sources=[]
        )
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
