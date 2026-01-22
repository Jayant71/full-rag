from langchain_chroma import Chroma
from app.embeddings.hg_embeddings import HuggingFaceEmbedding
from app.utils.logger import vector_store_logger as VL


class ChromadbVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "default_collection", embedding_function=HuggingFaceEmbedding, embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        embedding = embedding_function(model_name=embedding_model)
        self.db = Chroma(
            embedding_function=embedding.get_embeddings_model(),
            persist_directory=persist_directory,
            collection_name=collection_name,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None):
        self.db.add_texts(texts, metadatas)

    def similarity_search(self, query: str, k: int = 4):
        return self.db.similarity_search(query, k=k)

    def similarity_search_with_scores(self, query: str, k: int = 4):
        return self.db.similarity_search_with_score(query, k=k)


if __name__ == "__main__":

    db = ChromadbVectorStore(
        persist_directory="./chroma_db",
        collection_name="test_collection",
    )
    texts = [
        "Apple is looking at buying U.K. startup for $1 billion",
        "Autonomous cars shift insurance liability toward manufacturers",
        "San Francisco considers banning sidewalk delivery robots",
        "London is a big city in the United Kingdom",
    ]
    db.add_texts(texts)
    results = db.similarity_search_with_scores("What is London?", k=2)
    for i, res in enumerate(results):
        VL.debug(f"Result {i+1}: {res[0].page_content} with score {res[1]}")
        VL.debug("--------------------------------------")
