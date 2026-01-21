from pydoc import Doc
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
from app.utils.logger import documents_logger


def load_text_file(file_path: str):
    from langchain_community.document_loaders import TextLoader
    file = TextLoader(file_path, encoding='utf-8')
    documents = file.load()
    return documents


def load_pdf_file(file_path: str):
    from langchain_community.document_loaders import PyPDFLoader
    file = PyPDFLoader(file_path)
    documents = file.load()
    return documents


if __name__ == "__main__":
    file_path = "example.txt"
    text = load_text_file(file_path)

    content = ""
    documents_logger.info(f"Loaded {len(text)} documents from {file_path}")
    documents_logger.info(text[0].page_content)
    for doct in text:
        content += doct.page_content + " "
    document = Document(
        page_content=content,
        metadata={"source": "sample.txt"}
    )

    chunks = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=200,
        chunk_overlap=10,
    ).split_documents([document])

    for i, chunk in enumerate(chunks):
        documents_logger.info(
            f"Chunk {i + 1} content: {chunk.page_content}")
