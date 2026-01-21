from abc import ABC, abstractmethod


class EmbeddingGenerator(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        pass
