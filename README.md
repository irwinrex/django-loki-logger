# Loki Django Logger

This package provides a lightweight logging solution for Django applications that sends logs to Grafana Loki with gzip compression for improved performance.

## Installation

```bash
pip install loki-django-logger
```

## Configuration

1. Add the logger to your Django settings.

In your `settings.py`:

```python
from loki_django_logger.logger import configure_logger

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loki": {
            "class": "loki_django_logger.handler.AsyncGzipLokiHandler",
            "loki_url": "http://localhost:3100",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["loki"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
```

2. Install Loki if not already available:

```bash
docker run -d --name=loki -p 3100:3100 grafana/loki:latest
```

3. Run your Django application and monitor the logs in Loki.

## Example Usage

In your Django views or tasks:

```python
import logging
logger = logging.getLogger("django")

def sample_view(request):
    logger.info("Sample log message sent to Loki")
    return JsonResponse({"message": "Logged successfully!"})
```

## Testing

To run tests:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
