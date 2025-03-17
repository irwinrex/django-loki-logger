# logger.py
import logging
from .handler import AsyncGzipLokiHandler

def configure_logger(loki_url):
    logger = logging.getLogger("django")
    logger.setLevel(logging.INFO)

    handler = AsyncGzipLokiHandler(loki_url)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

# utils.py
import platform
import socket

def get_system_info():
    return {
        "os": platform.system(),
        "hostname": socket.gethostname(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0]
    }
