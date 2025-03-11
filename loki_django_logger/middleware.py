import logging
import time, requests
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

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
            "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
        }

        logger.info("API Request Log", extra=log_data)
        self.send_to_loki(log_data)
        return response

    def process_exception(self, request, exception):
        log_data = {
            "path": request.path,
            "method": request.method,
            "error": str(exception),
        }
        logger.error("API Exception Log", exc_info=True, extra=log_data)
        self.send_to_loki(log_data)

    def send_to_loki(self, log_data):
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
            response = requests.post(loki_url, json=payload, headers=headers, timeout=settings.LOGGING["handlers"]["loki"].get("timeout", 1))
            if response.status_code != 204:
                logger.error(f"Failed to send logs to Loki with status code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Failed to send logs to Loki: {e}")