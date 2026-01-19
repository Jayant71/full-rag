from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app import schemas, models
from app.database.database import get_session

router = APIRouter(
    prefix="/spaces",
    tags=["spaces"],
)


@router.post("/spaces", response_model=schemas.Space)
async def create_space(name: str, session: AsyncSession = Depends(get_session)):

    return schemas.Space(id=str(uuid.uuid4()), name=name)


@router.get("/spaces", response_model=List[schemas.Space])
async def list_spaces(session: AsyncSession = Depends(get_session)):
    # result = await session.execute(select(models.Space))
    # spaces = result.scalars().all()

    return []


@router.delete("/spaces/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    space_id: str,
    session: AsyncSession = Depends(get_session),
    user=Depends()
):
    return {"message": "Space deleted successfully"}
