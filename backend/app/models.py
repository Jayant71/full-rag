from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

# --- SQLModel Tables ---

class Space(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    documents: List["Document"] = Relationship(back_populates="space")
    messages: List["ChatMessage"] = Relationship(back_populates="space")

class Document(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str
    storage_key: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    space_id: uuid.UUID = Field(foreign_key="space.id")
    space: Space = Relationship(back_populates="documents")

class ChatMessage(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    space_id: uuid.UUID = Field(foreign_key="space.id")
    space: Space = Relationship(back_populates="messages")

# --- Pydantic API Models ---

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    # chat_history is now optional/deprecated as we fetch from DB, 
    # but keeping it for backward compat or explicit context injection if needed.
    chat_history: List[Message] = [] 

class Source(BaseModel):
    text: str
    score: Optional[float] = None
    metadata: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []

class IngestResponse(BaseModel):
    message: str
    filename: str

class AgentQueryRequest(BaseModel):
    query: str
    space_id: str # Agent must specify space


