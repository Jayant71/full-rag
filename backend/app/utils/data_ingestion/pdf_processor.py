from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.logger import documents_logger as DL
from app.utils.data_ingestion.base_processor import Processor


class PDFProcessor(Processor):

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def process(self, file_path: str):
        loader = PyMuPDFLoader(file_path, )
        documents = loader.load()

        all_chunks = self.text_splitter.split_documents(documents)

        for i, chunk in enumerate(all_chunks):
            chunk.metadata = {
                **chunk.metadata,

                "chunk_index": i + 1,
                "total_chunks": len(all_chunks)
            }

        return all_chunks


if __name__ == "__main__":
    pdf_processor = PDFProcessor(chunk_size=500, chunk_overlap=50)

    chunks = pdf_processor.process(r"E:\College\Mydocs\Results\sem8.pdf")

    for chunk in chunks:
        DL.debug("--------------------------------------")
        DL.debug(f"Chunk content: {chunk.metadata}")
        DL.debug("--------------------------------------")
