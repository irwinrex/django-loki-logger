import logging
import time
from loki_django_logger.logger import configure_logger
from loki_django_logger.handler import AsyncGzipLokiHandler

def test_logger_initialization():
    logger = configure_logger("https://loki.test.xyz/loki/api/v1/push")
    assert logger.name == "django"
    assert logger.level == logging.INFO
    assert any(isinstance(handler, AsyncGzipLokiHandler) for handler in logger.handlers)

def test_log_delivery(mocker):
    mock_post = mocker.patch("requests.post")  # Mock HTTP request to Loki

    logger = configure_logger("https://loki.test.xyz/loki/api/v1/push")
    logger.info("Test log message", extra={"user_id": 789})

    # Wait for the background thread to process logs
    time.sleep(2)

    assert mock_post.called
    assert "Test log message" in mock_post.call_args[1]["data"].decode('utf-8')
