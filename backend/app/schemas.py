from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class UserBase(BaseModel):
    id: str
    username: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class User(UserBase):
    email: str

    model_config = {
        "from_attributes": True
    }


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
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
    space_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class Space(BaseModel):
    id: str
    name: str

    model_config = {
        "from_attributes": True
    }


class Document(BaseModel):
    id: str
    filename: str
    storage_key: str
    space_id: str

    model_config = {
        "from_attributes": True
    }


class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    user_id: Optional[str] = None
    space_id: str

    model_config = {
        "from_attributes": True
    }
