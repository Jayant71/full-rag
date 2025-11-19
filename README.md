# Production-Grade Multi-Modal RAG System

This project implements a robust RAG system with a FastAPI backend, Streamlit frontend, and Qdrant vector database.

## Architecture
- **Backend**: FastAPI (Async)
- **Frontend**: Streamlit
- **Vector DB**: Qdrant
- **Orchestration**: Docker Compose
- **RAG Engine**: LlamaIndex (LlamaParse, OpenAI, Cohere Rerank)

## Prerequisites
- Docker & Docker Compose
- OpenAI API Key
- LlamaCloud API Key (for LlamaParse)
- Cohere API Key (Optional, for Reranking)

## Setup

1. **Clone the repository**

2. **Environment Variables**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   
   **Configuration Options:**
   - `ENV`: `dev` or `prod`
   - `DATABASE_TYPE`: `sqlite` (default) or `postgres`
   - `STORAGE_TYPE`: `local` (default) or `s3`
   
   **API Keys:**
   ```properties
   OPENAI_API_KEY=sk-...
   LLAMA_CLOUD_API_KEY=llx-...
   COHERE_API_KEY=...
   ```
   
   **Production Config (Postgres & MinIO):**
   ```properties
   POSTGRES_URL=postgresql://user:password@localhost:5400/ragdb
   S3_ENDPOINT_URL=http://localhost:9000
   S3_ACCESS_KEY=minioadmin
   S3_SECRET_KEY=minioadmin
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Usage

- **Frontend**: Access the chat interface at `http://localhost:8501`.
- **Backend API**: Access the API documentation at `http://localhost:8000/docs`.

### API Endpoints
- `POST /ingest`: Upload a file (PDF, DOCX, etc.) for ingestion.
- `POST /chat`: Chat with the RAG system.
- `POST /agent-query`: Simplified query endpoint for AI agents.

## Development

### Backend
```bash
cd backend
# Install dependencies including python-multipart
uv add -r requirements.txt
uv add python-multipart

# Run the server (make sure you are in the /backend directory)
uv run uvicorn app.api:app --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run ui.py
```
