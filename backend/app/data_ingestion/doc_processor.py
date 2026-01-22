from app.data_ingestion.base_processor import Processor
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader


class DocProcessor(Processor):

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def process(self, file_path: str):
        loader = Docx2txtLoader(file_path)
        try:
            documents = loader.load()
        except Exception as e:
            raise RuntimeError(f"Failed to load .docx file: {e}")

        all_chunks = self.text_splitter.split_documents(documents)

        for i, chunk in enumerate(all_chunks):
            chunk.metadata = {
                **chunk.metadata,
                "chunk_index": i + 1,
                "total_chunks": len(all_chunks)
            }

        return all_chunks


if __name__ == "__main__":
    doc_processor = DocProcessor(chunk_size=500, chunk_overlap=50)

    chunks = doc_processor.process(r"E:\College\Mydocs\Results\sample.docx")

    for chunk in chunks:
        print("--------------------------------------")
        print(f"Chunk content: {chunk.metadata}")
        print("--------------------------------------")
