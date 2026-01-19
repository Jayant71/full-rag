from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
import os

if settings.DATABASE_TYPE == "sqlite":
    os.makedirs("app_data", exist_ok=True)


def get_db_url():
    if settings.DATABASE_TYPE == "sqlite":
        return "sqlite:///./app_data/metadata.db"
    elif settings.DATABASE_TYPE == "postgres":
        if not settings.POSTGRES_URL:
            raise ValueError(
                "POSTGRES_URL must be set when DATABASE_TYPE is postgres")
        return settings.POSTGRES_URL
    else:
        raise ValueError(
            f"Unsupported DATABASE_TYPE: {settings.DATABASE_TYPE}")


engine = create_async_engine(get_db_url(), echo=(settings.ENV == "dev"))

sessionLocal = AsyncSession(engine, expire_on_commit=False, autocommit=False)

Base = declarative_base()


async def get_session():
    async with sessionLocal as session:
        try:
            yield session
        finally:
            await session.close()
