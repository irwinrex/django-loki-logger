# logger.py
import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class LokiLoggerHandler(logging.Handler):
    def __init__(self, loki_url, tags=None, timeout=1.0):
        super().__init__()
        self.loki_url = loki_url
        self.tags = tags or {"app": "django"}
        self.timeout = max(0.1, float(timeout))

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "streams": [
                {
                    "stream": self.tags,
                    "values": [
                        [str(int(time.time() * 1e9)), log_entry]
                    ],
                }
            ]
        }
        self.send_to_loki(payload)

    def send_to_loki(self, payload):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.loki_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
                if response.status_code == 204:
                    return
            except requests.RequestException as e:
                logger.warning(f"[Attempt {attempt + 1}/{retries}] Failed to send logs to Loki: {e}")
                time.sleep(2 ** attempt)

        logger.error(f"All {retries} retries failed. Logs not sent to Loki.")
