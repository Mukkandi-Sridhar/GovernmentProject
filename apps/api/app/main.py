from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_embedding_service
from app.logging_config import get_logger, setup_logging
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from app.routers import admin, public, system
from app.security.rate_limit import RateLimitMiddleware
from app.tasks.scheduler import SchedulerManager

settings = get_settings()
setup_logging()
logger = get_logger(__name__)

scheduler_manager = SchedulerManager(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    embedding_service = get_embedding_service()
    try:
        await asyncio.wait_for(embedding_service.load_snapshot(), timeout=20)
    except TimeoutError:
        logger.warning("FAISS snapshot load timed out during startup; continuing without snapshot")
    except Exception as exc:  # noqa: BLE001
        logger.warning("FAISS snapshot load failed during startup: %s", exc)

    try:
        await asyncio.wait_for(embedding_service.refresh_index_from_repository(), timeout=20)
    except TimeoutError:
        logger.warning("Embedding index refresh timed out during startup; continuing with empty index")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Embedding index refresh failed during startup: %s", exc)

    scheduler_manager.start()
    yield
    scheduler_manager.shutdown()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    default_requests_per_minute=settings.rate_limit_per_minute,
    chat_query_requests_per_minute=settings.rate_limit_chat_query_per_minute,
    chat_jobs_requests_per_minute=settings.rate_limit_chat_jobs_per_minute,
    admin_requests_per_minute=settings.rate_limit_admin_per_minute,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start

    path = request.url.path
    method = request.method
    status_code = str(response.status_code)

    REQUEST_COUNT.labels(method=method, path=path, status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
    return response


app.include_router(system.router)
app.include_router(public.router)
app.include_router(admin.router)

