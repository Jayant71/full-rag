import logging

logging.basicConfig(
    filename='app.log',
    filemode='w',
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='%(levelname)s - %(message)s',
    level=logging.DEBUG,
)

documents_logger = logging.getLogger("documents_logger")
documents_logger.setLevel(logging.DEBUG)
