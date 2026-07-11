"""Request logging middleware."""

import time

from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send

SKIP_PATHS = frozenset({"/health", "/health/live", "/health/ready"})


class RequestLoggingMiddleware:
    """ASGI middleware that logs HTTP requests with method, path, status, and duration."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in SKIP_PATHS:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        start = time.perf_counter()
        status_code = 0

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.bind(method=method, path=path, status_code=status_code, duration_ms=duration_ms).info("request")
