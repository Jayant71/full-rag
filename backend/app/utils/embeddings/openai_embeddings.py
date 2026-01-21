from app.utils.embeddings.base_embedding import EmbeddingGenerator
from app.utils.logger import documents_logger as DL
from app.utils.cosine_similarity import cosine_similarity
from langchain_openai.embeddings import OpenAIEmbeddings
from pydantic import SecretStr
from app.core.config import settings


class OpenAIEmbedding(EmbeddingGenerator):
    def __init__(self, model_name: str = "openai-embedding-001"):
        if settings.OPENAI_API_KEY is None:
            raise ValueError("Missing OPENAI_API_KEY")
        self.model = OpenAIEmbeddings(
            model=model_name, api_key=SecretStr(settings.OPENAI_API_KEY))

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        return self.model.embed_documents(["test"])[0].__len__()


if __name__ == "__main__":
    openai_embeddings = OpenAIEmbedding()

    texts = [
        "Cat", "Dog", "Elephant", "Kitten", "Puppy", "Lion", "Tiger", "Orange Cat", "Orange", "Grapes", "Wolf"
    ]

    embeddings = openai_embeddings.generate_embeddings(texts)
    # DL.debug(embeddings)

    for i, emb in enumerate(embeddings):
        DL.debug(f"Text: {texts[i]}")
        DL.debug(f"Embedding: {emb}")
        DL.debug("--------------------------------------")
    DL.debug(
        f"Embedding Dimension: {openai_embeddings.get_embedding_dimension()}")

    DL.debug(cosine_similarity(embeddings[0], embeddings[3]))  # Cat vs Kitten
    DL.debug(cosine_similarity(embeddings[1], embeddings[4]))  # Dog vs Puppy
    # Cat vs Orange Cat
    DL.debug(cosine_similarity(embeddings[0], embeddings[7]))
    DL.debug(cosine_similarity(embeddings[0], embeddings[1]))  # Cat vs Dog
    # Elephant vs Lion
    DL.debug(cosine_similarity(embeddings[2], embeddings[5]))
    # Grapes vs Wolf
    DL.debug(cosine_similarity(embeddings[9], embeddings[10]))
    # Orange vs Grapes
    DL.debug(cosine_similarity(embeddings[8], embeddings[9]))
    DL.debug(cosine_similarity(embeddings[5], embeddings[6]))  # Lion vs Tiger
    # Kitten vs Puppy
    DL.debug(cosine_similarity(embeddings[3], embeddings[4]))
