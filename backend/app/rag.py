from app.ingestion import Ingestion
from app.retriever import RetrievalPipeline
from app.llm.llm import get_openai_chat_model
from app.utils.logger import rag_logger as RL


def ingest_and_index(file_path: str, retrieval: RetrievalPipeline, file_type: str = 'pdf', isDirectory: bool = False):
    ingestion = Ingestion()
    chunks = ingestion.ingest(
        file_path, file_type=file_type, isDirectory=isDirectory)  # type: ignore
    retrieval.add_chunks(chunks)
    return len(chunks)


if __name__ == "__main__":

    retriever = RetrievalPipeline()
    # ingest_and_index(r"E:\College\Mydocs\Results\sem8.pdf",
    #                  retriever, file_type='pdf')

    while True:
        query = input("Enter your question (or 'q' to quit): ")
        if query.lower() == 'q':
            break
        chat_model = get_openai_chat_model()
        retrieved_chunks = retriever.retrieve(query)
        if not retrieved_chunks:
            print("No relevant documents found.")
            continue
        combined_context = "\n\n".join(
            [chunk.page_content for chunk in retrieved_chunks])
        prompt = f"Use the following context to answer the question:\n\n{combined_context}\n\nQuestion: {query}\nAnswer:"
        response = chat_model.invoke(prompt)

        RL.info(f"User Query: {query}")
        RL.info(f"Retrieved {len(retrieved_chunks)} chunks for the query.")
        RL.info(
            f"Retrieved Chunks Content: {[chunk.page_content for chunk in retrieved_chunks]}")
        RL.info(f"Response: {response.content}")
        for handler in RL.handlers:
            handler.flush()
