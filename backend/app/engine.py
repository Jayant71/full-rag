"""
RAG Engine with Per-User Configuration Support.

This module provides functions for document ingestion, chat, and query engines
that use per-user API keys and Qdrant URLs from the database.
"""
import os
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings as LlamaSettings,
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
from app.user_keys import UserAPIKeys

load_dotenv()
nest_asyncio.apply()


def get_vector_store(api_keys: UserAPIKeys) -> QdrantVectorStore:
    """Get the Qdrant vector store instance using user's Qdrant URL."""
    client = QdrantClient(url=api_keys.get_qdrant_url())
    return QdrantVectorStore(client=client, collection_name="rag_collection")


def get_qdrant_client(api_keys: UserAPIKeys) -> QdrantClient:
    """Get the Qdrant client instance using user's Qdrant URL."""
    return QdrantClient(url=api_keys.get_qdrant_url())


def get_index(api_keys: UserAPIKeys) -> VectorStoreIndex:
    """Get the vector store index using user's Qdrant URL."""
    vector_store = get_vector_store(api_keys)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )


def create_llm(api_keys: UserAPIKeys) -> OpenAI:
    """Create an OpenAI LLM instance with the given API keys."""
    return OpenAI(
        model="gpt-4o",
        api_key=api_keys.get_openai_key()
    )


def create_embed_model(api_keys: UserAPIKeys) -> OpenAIEmbedding:
    """Create an OpenAI embedding model with the given API keys."""
    return OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=api_keys.get_openai_key()
    )


async def ingest_document(
    file_path: str, 
    filename: str, 
    space_id: str,
    api_keys: UserAPIKeys
):
    """
    Ingest a document into the vector store.
    
    Args:
        file_path: Path to the file to ingest
        filename: Original filename
        space_id: Space ID for metadata filtering
        api_keys: User's API keys and Qdrant URL (required)
    """
    # Create parser with user's LlamaCloud key
    parser = LlamaParse(
        api_key=api_keys.get_llama_cloud_key(),
        result_type="markdown",
        verbose=True,
    )
    
    documents = await parser.aload_data(file_path)
    
    # Add metadata
    for doc in documents:
        doc.metadata["filename"] = filename
        doc.metadata["space_id"] = space_id
    
    # Create embedding model with user's OpenAI key
    embed_model = create_embed_model(api_keys)
    
    # Use user's Qdrant URL
    vector_store = get_vector_store(api_keys)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create index from documents (this will chunk and embed)
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    return f"Successfully ingested {filename}"


def get_chat_engine(space_id: str, api_keys: UserAPIKeys):
    """
    Get a chat engine for the given space.
    
    Args:
        space_id: Space ID for filtering documents
        api_keys: User's API keys and Qdrant URL (required)
    """
    # Create LLM with user's key
    llm = create_llm(api_keys)
    
    # Get index using user's Qdrant URL
    index = get_index(api_keys)
    
    # Configure reranker if Cohere key is available
    node_postprocessors = []
    cohere_key = api_keys.get_cohere_key()
    if cohere_key:
        reranker = CohereRerank(api_key=cohere_key, top_n=3)
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
        llm=llm,
    )


def get_query_engine(space_id: str, api_keys: UserAPIKeys):
    """
    Get a query engine for the given space.
    
    Args:
        space_id: Space ID for filtering documents
        api_keys: User's API keys and Qdrant URL (required)
    """
    # Create LLM with user's key
    llm = create_llm(api_keys)
    
    # Get index using user's Qdrant URL
    index = get_index(api_keys)
    
    node_postprocessors = []
    cohere_key = api_keys.get_cohere_key()
    if cohere_key:
        reranker = CohereRerank(api_key=cohere_key, top_n=3)
        node_postprocessors.append(reranker)
        
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="space_id", value=space_id)]
    )
        
    return index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=node_postprocessors,
        filters=filters,
        llm=llm,
    )


def delete_document_from_vector_store(space_id: str, filename: str, api_keys: UserAPIKeys):
    """Delete a document from the vector store by space_id and filename."""
    client = get_qdrant_client(api_keys)
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
