# Logger.py
import logging
import asyncio
import httpx
import time
from django.conf import settings

logger = logging.getLogger(__name__)

def get_timeout():
    try:
        return max(0.1, float(settings.LOGGING["handlers"]["loki"].get("timeout", 1)))
    except ValueError:
        return 1.0

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
        retries = 3
        for attempt in range(retries):
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
                    return
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                logger.warning(f"[Attempt {attempt + 1}/{retries}] Failed to send logs to Loki: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"All {retries} retries failed. Logs not sent to Loki.")
