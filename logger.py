import logging
import asyncio
import httpx
import time
from django.conf import settings

class LokiLoggerHandler(logging.Handler):
    def __init__(self, loki_url, tags=None):
        super().__init__()
        self.loki_url = loki_url
        self.tags = tags or {"app": "django"}

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
        asyncio.create_task(self.send_to_loki(payload))

    async def send_to_loki(self, payload):
        try:
            async with httpx.AsyncClient() as client:
                await asyncio.wait_for(
                    client.post(
                        self.loki_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=get_timeout()
                    ),
                    timeout=get_timeout()
                )
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            logger.error(f"Failed to send logs to Loki: {e}")