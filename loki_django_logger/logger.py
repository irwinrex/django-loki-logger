# logger.py
import logging
from .handler import AsyncGzipLokiHandler

def configure_logger(loki_url, labels=None, flush_interval=5):
    logger = logging.getLogger("django")
    logger.setLevel(logging.INFO)

    if not any(isinstance(h, AsyncGzipLokiHandler) for h in logger.handlers):
        handler = AsyncGzipLokiHandler(loki_url, labels=labels, flush_interval=flush_interval)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)

    return logger