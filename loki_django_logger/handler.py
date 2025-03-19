import logging
import queue
import threading
import requests
import gzip
import json
import time
import traceback

class AsyncGzipLokiHandler(logging.Handler):
    def __init__(self, loki_url, labels=None, flush_interval=5):
        super().__init__()
        self.loki_url = loki_url.rstrip('/')
        self.labels = labels or {"job": "django-logs"}
        self.flush_interval = flush_interval
        self.log_queue = queue.Queue()
        threading.Thread(target=self._process_logs, daemon=True).start()

    def formatTime(self, record, datefmt=None):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created))

    def emit(self, record):
        try:
            log_entry = {
                "level": record.levelname,
                "timestamp": self.formatTime(record),
                "message": record.getMessage(),
                "module": getattr(record, "module", "Unknown"),
                "traceback": self._format_exception(record),
                "status_code": getattr(record, "status_code", "Unknown")
            }

            # Add 'extra' details if provided
            log_entry.update(getattr(record, 'extra', {}))

            # Request data for richer context (optional)
            if hasattr(record, "request"):
                log_entry["path"] = record.request.get_full_path()
                log_entry["method"] = record.request.method
                log_entry["user_agent"] = record.request.META.get("HTTP_USER_AGENT")

            self.log_queue.put(log_entry)
        except Exception as e:
            logging.error(f"Failed to emit log: {e}")

    def _format_exception(self, record):
        return ''.join(traceback.format_exception(*record.exc_info)) if record.exc_info else None

    def _process_logs(self):
        log_buffer = []
        last_flush_time = time.time()

        while True:
            try:
                log_entry = self.log_queue.get(timeout=self.flush_interval)
                log_buffer.append(log_entry)
            except queue.Empty:
                pass

            if log_buffer and (time.time() - last_flush_time >= self.flush_interval):
                self._send_logs(log_buffer)
                log_buffer.clear()
                last_flush_time = time.time()

    def _send_logs(self, log_buffer):
        try:
            payload = {
                "streams": [{
                    "stream": self.labels,
                    "values": [
                        [str(int(time.time() * 1e9)), json.dumps(log)] for log in log_buffer
                    ]
                }]
            }

            compressed_payload = gzip.compress(json.dumps(payload).encode('utf-8'))
            headers = {"Content-Encoding": "gzip", "Content-Type": "application/json"}

            response = requests.post(f"{self.loki_url}/loki/api/v1/push",
                                     data=compressed_payload,
                                     headers=headers)
            if response.status_code != 204:
                logging.error(f"Failed to send logs to Loki: {response.status_code}, {response.text}")
        except Exception as e:
            logging.error(f"Error sending logs to Loki: {e}")
