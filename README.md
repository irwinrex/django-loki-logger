# Loki Django Logger

Loki Django Logger is a lightweight and efficient logger designed to send logs to Grafana Loki directly from your Django application with minimal latency and low resource consumption. It supports dynamic configurations, timeout management, and efficient logging using `asyncio` and `httpx`.

## Features
- Asynchronous log transmission for improved performance
- Configurable timeout to prevent delayed requests
- Middleware for capturing request/response data with latency tracking
- Customizable tags for better log organization in Loki

## Installation
```bash
pip install loki-django-logger
```

## Configuration
### 1. Add Middleware
Add the following middleware to your `settings.py`:

```python
MIDDLEWARE = [
    ...,
    "loki_django_logger.middleware.LokiLoggerMiddleware",
]
```

### 2. Add Logging Configuration
Add the Loki logger configuration in `settings.py`:

```python
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
```

### 3. Environment Variables (Optional)
For improved flexibility, consider using environment variables for sensitive information like the `loki_url` or timeout.

```env
LOKI_URL=http://localhost:3100/loki/api/v1/push
LOGGING_TIMEOUT=1
```

## Usage
Once integrated, logs will automatically be sent to your Loki instance with the following details:
- API endpoint path
- HTTP method
- Response status code
- Time taken for the request
- Client IP address

## Example Log Output
```json
{
    "path": "/api/v1/patient",
    "method": "POST",
    "status_code": 200,
    "duration": 0.123,
    "client_ip": "192.168.1.100"
}
```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License.