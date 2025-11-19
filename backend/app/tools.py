from llama_index.core.tools import FunctionTool
from app.engine import get_query_engine

def rag_query(query: str) -> str:
    """
    Queries the RAG system to retrieve information from the knowledge base.
    Useful for answering questions based on uploaded documents.
    """
    query_engine = get_query_engine()
    response = query_engine.query(query)
    return str(response)

rag_tool = FunctionTool.from_defaults(
    fn=rag_query,
    name="rag_query_tool",
    description="Queries the RAG system for information."
)

