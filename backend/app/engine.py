import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document,
)
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_parse import LlamaParse
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import nest_asyncio
from app.config import settings

load_dotenv()
nest_asyncio.apply()

# Initialize Settings
Settings.llm = OpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)

def get_vector_store():
    client = QdrantClient(url=settings.QDRANT_URL)
    return QdrantVectorStore(client=client, collection_name="rag_collection")

def get_qdrant_client():
    return QdrantClient(url=settings.QDRANT_URL)

def get_index():
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

async def ingest_document(file_path: str, filename: str, space_id: str):
    parser = LlamaParse(
        api_key=settings.LLAMA_CLOUD_API_KEY,
        result_type="markdown",
        verbose=True,
    )
    
    documents = await parser.aload_data(file_path)
    
    # Add metadata
    for doc in documents:
        doc.metadata["filename"] = filename
        doc.metadata["space_id"] = space_id
    
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create index from documents (this will chunk and embed)
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )
    return f"Successfully ingested {filename}"

def get_chat_engine(space_id: str):
    index = get_index()
    
    # Configure reranker if key is available
    node_postprocessors = []
    if settings.COHERE_API_KEY:
        reranker = CohereRerank(api_key=settings.COHERE_API_KEY, top_n=3)
        node_postprocessors.append(reranker)
    
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="space_id", value=space_id)]
    )
    
    return index.as_chat_engine(
        chat_mode="context",
        similarity_top_k=10,
        node_postprocessors=node_postprocessors,
        filters=filters,
        verbose=True,
    )

def get_query_engine(space_id: str):
    index = get_index()
    
    node_postprocessors = []
    if settings.COHERE_API_KEY:
        reranker = CohereRerank(api_key=settings.COHERE_API_KEY, top_n=3)
        node_postprocessors.append(reranker)
        
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="space_id", value=space_id)]
    )
        
    return index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=node_postprocessors,
        filters=filters,
    )

def delete_document_from_vector_store(space_id: str, filename: str):
    client = get_qdrant_client()
    client.delete(
        collection_name="rag_collection",
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="space_id",
                        match=models.MatchValue(value=space_id),
                    ),
                    models.FieldCondition(
                        key="filename",
                        match=models.MatchValue(value=filename),
                    ),
                ]
            )
        ),
    )


