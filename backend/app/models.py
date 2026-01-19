from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy import UUID as SQLAlchemyUUID
from datetime import datetime
import uuid
from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(SQLAlchemyUUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    messages = relationship("ChatMessage", back_populates="user")


class Space(Base):
    __tablename__ = "spaces"

    id = Column(SQLAlchemyUUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)

    documents = relationship("Document", back_populates="space")
    messages = relationship("ChatMessage", back_populates="space")


class Document(Base):
    __tablename__ = "documents"

    id = Column(SQLAlchemyUUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True)
    filename = Column(String)
    storage_key = Column(String)
    uploaded_at = Column(DateTime, default=datetime.now)
    space_id = Column(ForeignKey("spaces.id"))
    space = relationship("Space", back_populates="documents")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(SQLAlchemyUUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", back_populates="messages")
    space_id = Column(ForeignKey("spaces.id"))
    space = relationship("Space", back_populates="messages")
