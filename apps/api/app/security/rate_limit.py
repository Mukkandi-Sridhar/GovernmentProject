from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        default_requests_per_minute: int,
        chat_query_requests_per_minute: int,
        chat_jobs_requests_per_minute: int,
        admin_requests_per_minute: int,
    ) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.default_requests_per_minute = default_requests_per_minute
        self.chat_query_requests_per_minute = chat_query_requests_per_minute
        self.chat_jobs_requests_per_minute = chat_jobs_requests_per_minute
        self.admin_requests_per_minute = admin_requests_per_minute
        self._buckets: dict[str, Deque[float]] = defaultdict(deque)

    def _bucket_and_limit(self, path: str) -> tuple[str, int]:
        if path == "/api/v1/chat/query":
            return "chat_query", self.chat_query_requests_per_minute
        if path.startswith("/api/v1/chat/jobs/"):
            return "chat_jobs", self.chat_jobs_requests_per_minute
        if path.startswith("/api/v1/admin/"):
            return "admin", self.admin_requests_per_minute
        return path, self.default_requests_per_minute

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        bucket_name, limit = self._bucket_and_limit(request.url.path)
        key = f"{request.client.host if request.client else 'unknown'}:{bucket_name}"
        now = time.time()
        bucket = self._buckets[key]

        while bucket and now - bucket[0] > 60:
            bucket.popleft()

        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        bucket.append(now)
        return await call_next(request)

