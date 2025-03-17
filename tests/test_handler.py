import logging
from loki_django_logger.logger import configure_logger

def test_logger_initialization():
    logger = configure_logger("https://loki.test.xyz/loki/api/v1/push")
    assert logger.name == "django"
    assert logger.level == logging.INFO
