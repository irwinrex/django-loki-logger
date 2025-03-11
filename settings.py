from loki_django_logger.logger import LokiLoggerHandler

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loki": {
            "level": "INFO",
            "class": "loki_django_logger.logger.LokiLoggerHandler",
            "loki_url": "http://localhost:3100/loki/api/v1/push",
            "tags": {"app": "django", "environment": "production"},
            "timeout": 2.0,  # Custom timeout passed as an argument
        },
    },
    "root": {
        "handlers": ["loki"],
        "level": "INFO",
    },
}
