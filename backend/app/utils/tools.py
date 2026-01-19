from llama_index.core.tools import FunctionTool


def rag_query(query: str) -> str:

    return "This is a placeholder response from the RAG system."


rag_tool = FunctionTool.from_defaults(
    fn=rag_query,
    name="rag_query_tool",
    description="Queries the RAG system for information."
)
