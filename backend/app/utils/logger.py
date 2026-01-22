import logging
import sys

file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '%(name)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)

stream_handler_stdout = logging.StreamHandler(sys.stdout)
stream_handler_stdout.setFormatter(logging.Formatter(
    '%(name)s - %(levelname)s - %(message)s'))
stream_handler_stdout.setLevel(logging.INFO)

stream_handler_file = logging.StreamHandler(
    open('app.log', 'a', encoding='utf-8'))
stream_handler_file.setFormatter(logging.Formatter(
    '%(name)s - %(levelname)s - %(message)s'))
stream_handler_file.setLevel(logging.INFO)


logging.basicConfig(
    handlers=[file_handler, stream_handler_file], force=True)

documents_logger = logging.getLogger("documents_logger")
documents_logger.setLevel(logging.INFO)

vector_store_logger = logging.getLogger("vector_store_logger")
vector_store_logger.setLevel(logging.INFO)


llm_logger = logging.getLogger("llm_logger")
llm_logger.setLevel(logging.INFO)

rag_logger = logging.getLogger("rag_logger")
rag_logger.setLevel(logging.INFO)
