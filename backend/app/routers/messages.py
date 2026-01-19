from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models
from app.database.database import get_session

router = APIRouter(
    prefix="/spaces/messages",
    tags=["messages"],
)


@router.get("/spaces/{space_id}/messages", response_model=List[schemas.ChatMessage])
async def get_messages(space_id: str, session: AsyncSession = Depends(get_session)):

    return []


@router.delete("/spaces/{space_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
async def clear_messages(space_id: str, session: AsyncSession = Depends(get_session)):

    return {"message": f"Cleared messages"}


@router.post("/agent-query")
async def agent_query(
    request: schemas.AgentQueryRequest,
    user: schemas.User = Depends()
):
    return {"answer": "This is a placeholder agent response."}
