import logging


def create_logger() -> logging.Logger:
    # logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    return logger
