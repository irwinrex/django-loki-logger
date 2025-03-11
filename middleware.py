import logging
import time
import asyncio
import httpx
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

def get_timeout():
    try:
        return max(0.1, float(settings.LOGGING["handlers"]["loki"].get("timeout", 1)))
    except ValueError:
        return 1.0

class LokiLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = round(time.time() - getattr(request, 'start_time', time.time()), 4)
        log_data = {
            "path": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration": duration,
            "client_ip": request.META.get("REMOTE_ADDR", "Unknown"),
        }

        logger.info("API Request Log", extra=log_data)
        asyncio.create_task(self.send_to_loki(log_data))
        return response

    def process_exception(self, request, exception):
        log_data = {
            "path": request.path,
            "method": request.method,
            "error": str(exception),
        }
        logger.error("API Exception Log", extra=log_data)
        asyncio.create_task(self.send_to_loki(log_data))

    async def send_to_loki(self, log_data):
        loki_url = settings.LOGGING["handlers"]["loki"]["loki_url"]
        headers = {"Content-Type": "application/json"}

        payload = {
            "streams": [
                {
                    "stream": settings.LOGGING["handlers"]["loki"].get("tags", {"app": "django"}),
                    "values": [
                        [str(int(time.time() * 1e9)), str(log_data)]
                    ],
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                await asyncio.wait_for(
                    client.post(loki_url, json=payload, headers=headers, timeout=get_timeout()),
                    timeout=get_timeout()
                )
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            logger.error(f"Failed to send logs to Loki: {e}")