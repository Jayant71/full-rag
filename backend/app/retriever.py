from pydoc import text
from app.vector_storage.chromadb import ChromadbVectorStore


class RetrievalPipeline:
    def __init__(self, vector_store: ChromadbVectorStore = ChromadbVectorStore()):
        self.vector_store = vector_store
        self.chunk_texts = []
        self.chunk_metadatas = []

    def add_chunks(self, chunks):
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        self.chunk_texts.extend(texts)
        self.chunk_metadatas.extend(metadatas)
        self.vector_store.add_texts(texts, metadatas)

    def retrieve(self, query: str, k: int = 4):
        query = query.strip()
        results = self.vector_store.similarity_search(query, k=k)
        return results
