# Loki Django Logger

A lightweight logging solution for Django applications that sends logs to Grafana Loki with gzip compression for improved performance.

## 🚀 Installation

Install the package using pip:

```bash
pip install loki-django-logger
```

## ⚙️ Configuration

### Add the logger to your Django settings

In your `settings.py` file:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "loki": {
            "class": "loki_django_logger.handler.AsyncGzipLokiHandler",
            "loki_url": "https://loki.test.dev",
            "labels": {"application": "django-app", "environment": "development"},
            "level": "DEBUG",
            "flush_interval": 1,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "loki"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

### Install Loki (if not already available)

```bash
docker run -d --name=loki -p 3100:3100 grafana/loki:latest
```

### Run your Django application and monitor the logs in Loki.

---

## 📝 Example Usage

In your Django views or tasks:

```python
import logging
logger = logging.getLogger("django")

def sample_view(request):
    logger.info("Sample log message sent to Loki", extra={"user_id": 123, "operation": "sample_view"})
    return JsonResponse({"message": "Logged successfully!"})
```

---

## 🧪 Testing

To run tests:

```bash
pytest tests/
```

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

