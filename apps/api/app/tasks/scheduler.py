from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings
from app.dependencies import get_embedding_service, get_ingestion_service
from app.logging_config import get_logger

logger = get_logger(__name__)


class SchedulerManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    async def daily_pipeline(self) -> None:
        ingestion = get_ingestion_service()
        embedding_service = get_embedding_service()
        result = await ingestion.run(actor="scheduler")
        logger.info("Daily pipeline finished: discovered=%s updated=%s", result.discovered, result.updated)

        # Reindex approved content after each scheduled run.
        count = await embedding_service.refresh_index_from_repository()
        await embedding_service.save_snapshot()
        logger.info("FAISS index refreshed with %s approved chunks", count)

    def start(self) -> None:
        if not self.settings.scheduler_enabled:
            logger.info("Scheduler disabled")
            return

        self.scheduler.add_job(
            self.daily_pipeline,
            trigger="cron",
            hour=self.settings.scheduler_cron_hour,
            minute=self.settings.scheduler_cron_minute,
            id="daily-crawl-job",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

