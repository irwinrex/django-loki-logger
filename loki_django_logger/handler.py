import logging
import queue
import threading
import requests
import gzip
import json
import time
import platform
import socket
import traceback

class AsyncGzipLokiHandler(logging.Handler):
    def __init__(self, loki_url, labels=None):
        super().__init__()
        self.loki_url = loki_url
        self.labels = labels or {"job": "django-logs"}
        self.log_queue = queue.Queue()
        threading.Thread(target=self._process_logs, daemon=True).start()

    def formatTime(self, record, datefmt=None):
        """
        Override formatTime to specify how to format the timestamp.
        This uses the standard format or you can specify your custom format.
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(record.created))

    def emit(self, record):
        try:
            log_entry = {
                "level": record.levelname,
                "timestamp": self.formatTime(record),  # Calls the overridden method
                "message": record.getMessage(),
                "module": record.module,
                "traceback": getattr(record, 'exc_text', None),
                "os": platform.system(),
                "device": socket.gethostname()
            }
            self.log_queue.put(log_entry)
        except Exception as e:
            print(f"Error formatting log record: {e}")

    def _process_logs(self):
        while True:
            try:
                log_entry = self.log_queue.get()
                payload = {
                    "streams": [
                        {
                            "stream": self.labels,
                            "values": [
                                [str(int(time.time() * 1e9)), json.dumps(log_entry)]
                            ]
                        }
                    ]
                }
                compressed_payload = gzip.compress(json.dumps(payload).encode('utf-8'))
                headers = {
                    "Content-Encoding": "gzip",
                    "Content-Type": "application/json"
                }
                response = requests.post(
                    f"{self.loki_url}/loki/api/v1/push",
                    data=compressed_payload,
                    headers=headers,
                    timeout=5
                )
                if response.status_code != 204:
                    print(f"Failed to send log to Loki: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error sending log: {e}")
