from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
import os

# Ensure app_data directory exists for SQLite
if settings.DATABASE_TYPE == "sqlite":
    os.makedirs("app_data", exist_ok=True)

def get_db_url():
    if settings.DATABASE_TYPE == "sqlite":
        return "sqlite:///./app_data/metadata.db"
    elif settings.DATABASE_TYPE == "postgres":
        if not settings.POSTGRES_URL:
            raise ValueError("POSTGRES_URL must be set when DATABASE_TYPE is postgres")
        return settings.POSTGRES_URL
    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {settings.DATABASE_TYPE}")

engine = create_engine(get_db_url(), echo=(settings.ENV == "dev"))

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
