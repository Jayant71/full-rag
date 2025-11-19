import os
import shutil
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select
from app.models import (
    ChatRequest, ChatResponse, IngestResponse, AgentQueryRequest, Source, 
    Space, Document, ChatMessage
)
from app.engine import ingest_document, get_chat_engine, get_query_engine
from app.db import get_session, init_db
from app.storage import get_storage_engine
from llama_index.core.llms import ChatMessage as LlamaChatMessage, MessageRole
import uuid

app = FastAPI(title="RAG API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "RAG Backend is running"}

# --- Spaces Endpoints ---

@app.post("/spaces", response_model=Space)
async def create_space(name: str, session: Session = Depends(get_session)):
    space = Space(name=name)
    session.add(space)
    session.commit()
    session.refresh(space)
    return space

@app.get("/spaces", response_model=List[Space])
async def list_spaces(session: Session = Depends(get_session)):
    spaces = session.exec(select(Space)).all()
    return spaces

# --- Documents Endpoints ---

@app.get("/spaces/{space_id}/documents", response_model=List[Document])
async def list_documents(space_id: str, session: Session = Depends(get_session)):
    # Verify space exists
    space = session.get(Space, uuid.UUID(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    documents = session.exec(select(Document).where(Document.space_id == space.id)).all()
    return documents

@app.delete("/spaces/{space_id}/documents/{document_id}")
async def delete_document(
    space_id: str, 
    document_id: str, 
    session: Session = Depends(get_session)
):
    # Verify space exists
    space = session.get(Space, uuid.UUID(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    # Verify document exists
    doc = session.get(Document, uuid.UUID(document_id))
    if not doc or doc.space_id != space.id:
        raise HTTPException(status_code=404, detail="Document not found in this space")

    try:
        # 1. Delete from Vector DB
        from app.engine import delete_document_from_vector_store
        delete_document_from_vector_store(space_id, doc.filename)
        
        # 2. Delete from Storage (Optional, but good practice)
        # storage = get_storage_engine()
        # storage.delete(doc.storage_key) # Assuming storage engine has delete
        
        # 3. Delete from SQL DB
        session.delete(doc)
        session.commit()
        
        return {"message": f"Deleted document {doc.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Ingestion ---

@app.post("/ingest/{space_id}", response_model=List[IngestResponse])
async def ingest_files(
    space_id: str, 
    files: List[UploadFile] = File(...), 
    session: Session = Depends(get_session)
):
    # Verify space exists
    space = session.get(Space, uuid.UUID(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    responses = []
    
    for file in files:
        if not file.filename:
            continue
            
        try:
            # 1. Save to temp for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
                
            # 2. Upload to Storage Engine (S3/Local)
            storage = get_storage_engine()
            storage_key = storage.upload(tmp_path, file.filename)
            
            # 3. Ingest into Vector DB (LlamaIndex)
            message = await ingest_document(tmp_path, file.filename, space_id)
            
            # 4. Save to SQL DB
            doc = Document(
                filename=file.filename,
                storage_key=storage_key,
                space_id=space.id
            )
            session.add(doc)
            session.commit()
            
            # Clean up temp file
            os.remove(tmp_path)
            
            responses.append(IngestResponse(message=message, filename=file.filename))
        except Exception as e:
            # Log error but maybe continue with other files? 
            # For now, we'll just raise to be safe or append error message
            responses.append(IngestResponse(message=f"Error: {str(e)}", filename=file.filename))
            
    return responses

# --- Chat ---

@app.post("/chat/{space_id}", response_model=ChatResponse)
async def chat(
    space_id: str, 
    request: ChatRequest, 
    session: Session = Depends(get_session)
):
    # Verify space exists
    space = session.get(Space, uuid.UUID(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    try:
        # 1. Fetch Chat History from DB
        # We retrieve the last N messages for context if needed, or rely on LlamaIndex's memory if we were using it fully.
        # For this implementation, we will fetch history to pass to the engine if we were doing stateless chat,
        # but since we are using `chat_engine.chat(query)`, it manages its own context usually. 
        # HOWEVER, with `as_chat_engine(chat_mode="context")`, it retrieves context from the index.
        # To support conversation history (multi-turn), we should ideally pass the history to the chat engine.
        
        # Let's fetch recent messages from SQL to construct the history for the LLM if needed, 
        # but LlamaIndex's `chat` method handles the immediate turn. 
        # If we want to persist conversation across requests, we need to pass `chat_history` to `chat_engine.chat`.
        
        db_messages = session.exec(select(ChatMessage).where(ChatMessage.space_id == space.id).order_by(ChatMessage.timestamp)).all()
        history = [
            LlamaChatMessage(role=MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT, content=msg.content)
            for msg in db_messages
        ]
        
        chat_engine = get_chat_engine(space_id)
        
        # 2. Query LlamaIndex
        # We pass the history so the model knows previous context
        response = chat_engine.chat(request.query, chat_history=history)
        
        # 3. Save new messages to DB
        user_msg = ChatMessage(role="user", content=request.query, space_id=space.id)
        ai_msg = ChatMessage(role="assistant", content=str(response), space_id=space.id)
        session.add(user_msg)
        session.add(ai_msg)
        session.commit()
        
        sources = []
        for node in response.source_nodes:
            sources.append(Source(
                text=node.node.get_content(),
                score=node.score,
                metadata=node.node.metadata
            ))
            
        return ChatResponse(answer=str(response), sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-query")
async def agent_query(request: AgentQueryRequest):
    try:
        query_engine = get_query_engine(request.space_id)
        response = query_engine.query(request.query)
        return {"response": str(response), "source_nodes": [node.node.metadata for node in response.source_nodes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


