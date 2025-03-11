MIDDLEWARE = [
    ...,
    "loki_django_logger.middleware.LokiLoggerMiddleware",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loki": {
            "level": "INFO",
            "class": "loki_django_logger.logger.LokiLoggerHandler",
            "loki_url": "http://localhost:3100/loki/api/v1/push",
            "tags": {"app": "django", "environment": "production"},
            "timeout": "1",  # Timeout in seconds
        },
    },
    "root": {
        "handlers": ["loki"],
        "level": "INFO",
    },
}
