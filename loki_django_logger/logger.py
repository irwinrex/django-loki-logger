# logger.py
import logging
import requests
import time
import json
import traceback
import sys
from django.conf import settings

logger = logging.getLogger(__name__)

class LokiLoggerHandler(logging.Handler):
    def __init__(self, loki_url, tags=None, timeout=1.0):
        super().__init__()
        self.loki_url = loki_url.rstrip('/')
        self.tags = tags or {"app": "django"}
        self.timeout = max(0.1, float(timeout))
        self.session = requests.Session()

    def emit(self, record):
        current_time = time.time()
        timestamp = int(current_time * 1e9)
        
        # Build structured log data, using extra attributes from the log record.
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": timestamp,
            "path": getattr(record, "path", "N/A"),
            "method": getattr(record, "method", "N/A"),
            "status_code": getattr(record, "status_code", "N/A"),
            "duration": getattr(record, "duration", "N/A"),
            "client_ip": getattr(record, "client_ip", "N/A"),
            "user_agent": getattr(record, "user_agent", "N/A"),
        }
        # Include traceback if available.
        if record.exc_info:
            log_data["traceback"] = ''.join(traceback.format_exception(*record.exc_info))
        elif record.levelno >= logging.ERROR:
            exc_info = sys.exc_info()
            if exc_info != (None, None, None):
                log_data["traceback"] = ''.join(traceback.format_exception(*exc_info))
        
        log_entry = json.dumps(log_data)
        payload = {
            "streams": [
                {
                    "stream": self.tags,
                    "values": [
                        [str(timestamp), log_entry]
                    ],
                }
            ]
        }
        self.send_to_loki(payload)

    def send_to_loki(self, payload):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.post(
                    self.loki_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
            except requests.RequestException as e:
                logger.warning(f"[Attempt {attempt + 1}/{retries}] Failed to send logs to Loki: {e}")
            else:
                if response.status_code == 204:
                    return
                logger.error(f"[Attempt {attempt + 1}/{retries}] Unexpected status code {response.status_code}")
            time.sleep(2 ** attempt)
        logger.error("All attempts failed. Logs not sent to Loki.")
