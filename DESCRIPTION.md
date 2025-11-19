# Retrieval Augmented Generation (RAG) System

## Overview
This project implements a state-of-the-art **Retrieval Augmented Generation (RAG)** system designed for flexibility, scalability, and data isolation. It leverages modern AI frameworks and infrastructure to provide a robust platform for document ingestion, semantic search, and conversational AI.

## Key Capabilities

### 1. Multi-Tenancy with "Spaces"
The system introduces the concept of **Spaces** to ensure data isolation and logical separation of content.
- **Isolation**: Documents and chat history are strictly scoped to a specific Space.
- **Use Cases**: Ideal for managing distinct projects, clients, or departments within a single deployment.
- **Management**: Users can create, list, and switch between Spaces seamlessly via the UI or API.

### 2. Advanced RAG Engine
Powered by **LlamaIndex**, the core engine delivers high-quality retrieval and generation:
- **Vector Search**: Uses **Qdrant**, a high-performance vector database, for fast and accurate semantic search.
- **Parsing**: Integrates **LlamaParse** for state-of-the-art document parsing (handling complex PDFs, tables, etc.).
- **Embeddings**: Utilizes OpenAI's latest embedding models (e.g., `text-embedding-3-small`) for deep semantic understanding.
- **Reranking**: Optional integration with **Cohere Rerank** to refine retrieval results and improve answer accuracy.
- **Metadata Filtering**: Enforces Space isolation at the database level using strict metadata filters.

### 3. Infrastructure Agnosticism
The system is designed to run anywhere, from a local laptop to a cloud cluster, with switchable infrastructure components configured via environment variables:
- **Database Layer**:
    - **SQLite**: Zero-config setup for local development.
    - **PostgreSQL**: Robust, concurrent relational database for production deployments.
- **Storage Layer**:
    - **Local Filesystem**: Simple file storage for development.
    - **S3 / MinIO**: Scalable object storage for production, supporting AWS S3 or self-hosted MinIO.

### 4. Full-Stack Orchestration
- **Backend**: Built with **FastAPI**, offering high-performance async endpoints, auto-generated Swagger documentation, and type safety with Pydantic.
- **Frontend**: A user-friendly **Streamlit** interface for managing Spaces, uploading documents, and chatting with your data.
- **Docker Compose**: Complete container orchestration for all services (Backend, Frontend, Qdrant, PostgreSQL, MinIO), ensuring consistent environments.

## Technical Architecture

### Backend (`/backend`)
- **API**: Exposes REST endpoints for Spaces, Ingestion, and Chat.
- **Engine**: Encapsulates LlamaIndex logic for indexing and retrieval.
- **Database**: Uses **SQLModel** (SQLAlchemy + Pydantic) for ORM.
- **Storage**: Implements a Strategy pattern to switch between Local and S3 storage providers.

### Frontend (`/frontend`)
- **Interactive UI**: Built with Streamlit for rapid interactivity.
- **Session Management**: Handles user session state for chat history and active Space selection.
- **API Integration**: Communicates with the backend via standard HTTP requests.

### Data Flow
1.  **Ingestion**:
    - User uploads a file to a Space.
    - File is stored in the configured Storage provider (Local/S3).
    - LlamaParse extracts text and structure.
    - Text is chunked and embedded by OpenAI.
    - Vectors + Metadata (Space ID) are stored in Qdrant.
    - Document metadata is recorded in the SQL Database.
2.  **Retrieval & Generation**:
    - User asks a question in a Space.
    - Query is embedded and sent to Qdrant with a Space ID filter.
    - Top-k relevant chunks are retrieved (and optionally reranked).
    - LLM (GPT-4o) synthesizes an answer using the retrieved chunks as context.
    - Chat history and response are saved to the SQL Database.

## API Reference
- `GET /spaces`: List all available Spaces.
- `POST /spaces`: Create a new Space.
- `POST /ingest/{space_id}`: Upload and ingest documents into a specific Space.
- `GET /spaces/{space_id}/documents`: List documents in a Space.
- `DELETE /spaces/{space_id}/documents/{doc_id}`: Delete a document.
- `POST /chat/{space_id}`: Conversational endpoint with context retention.
- `POST /agent-query`: Simplified endpoint for external AI agents.
