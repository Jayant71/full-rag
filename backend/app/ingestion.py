from typing import Literal, Optional
import os


class Ingestion:
    def __init__(self):
        pass

    def __process(self, file_path: str):
        if file_path.endswith('.pdf'):
            from app.data_ingestion.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            return processor.process(file_path)
        elif file_path.endswith('.docx'):
            from app.data_ingestion.doc_processor import DocProcessor
            processor = DocProcessor()
            return processor.process(file_path)
        elif file_path.endswith('.txt'):
            from app.data_ingestion.text_processor import TextProcessor
            processor = TextProcessor()
            return processor.process(file_path)
        else:
            raise ValueError(f"Unsupported file type for file: {file_path}")

    def ingest(self, file_path: str, file_type: Literal['pdf', 'docx', 'txt'] = 'pdf', isDirectory: bool = False):
        all_chunks = []
        if isDirectory:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    if file.lower().endswith(f".{file_type}"):
                        full_path = os.path.join(root, file)
                        chunks = self.__process(full_path)
                        all_chunks.extend(chunks)
        else:
            all_chunks = self.__process(file_path)

        return all_chunks


if __name__ == "__main__":
    ingestion = Ingestion()
    print(dir(ingestion))
