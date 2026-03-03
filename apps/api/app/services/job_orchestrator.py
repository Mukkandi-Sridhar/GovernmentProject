from __future__ import annotations

import asyncio

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import BackgroundTasks

from app.db.repository import Repository
from app.logging_config import get_logger
from app.models.schemas import ChatJobStatusResponse, CrawlJobRecord
from app.services.ingestion import IngestionPipelineService

logger = get_logger(__name__)


class JobOrchestratorService:
    def __init__(
        self,
        repository: Repository,
        ingestion_service: IngestionPipelineService,
    ) -> None:
        self.repository = repository
        self.ingestion_service = ingestion_service

    async def create_queued_job(
        self,
        trigger_source: str,
        trigger_user: str,
        intent_context: str | None,
    ) -> CrawlJobRecord:
        job = CrawlJobRecord(
            job_id=str(uuid4()),
            started_at=datetime.now(timezone.utc),
            status="queued",
            progress_phase="queued",
            trigger_source=trigger_source,
            trigger_user=trigger_user,
            intent_context=intent_context,
        )
        await self.repository.create_crawl_job(job)
        return job

    async def _run_collection_job(
        self,
        job_id: str,
        actor: str,
        trigger_source: str,
        trigger_user: str,
        intent_context: str | None,
    ) -> None:
        try:
            await self.ingestion_service.run(
                actor=actor,
                trigger_source=trigger_source,
                trigger_user=trigger_user,
                intent_context=intent_context,
                job_id=job_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Collection job failed for %s: %s", job_id, exc)
            await self.repository.update_crawl_job(
                job_id,
                status="failed",
                progress_phase="failed",
                error=str(exc),
                error_code="collection_failed",
                ended_at=datetime.now(timezone.utc),
            )

    async def trigger_collection_from_chat(
        self,
        user_id: str,
        intent_context: str,
        background_tasks: BackgroundTasks | None,
    ) -> CrawlJobRecord:
        job = await self.create_queued_job(
            trigger_source="chat",
            trigger_user=user_id,
            intent_context=intent_context,
        )

        if background_tasks is not None:
            background_tasks.add_task(
                self._run_collection_job,
                job.job_id,
                "chat-agent",
                "chat",
                user_id,
                intent_context,
            )
        else:
            asyncio.create_task(
                self._run_collection_job(
                    job.job_id,
                    "chat-agent",
                    "chat",
                    user_id,
                    intent_context,
                )
            )

        return job

    async def get_job_status(self, job_id: str) -> ChatJobStatusResponse | None:
        job = await self.repository.get_crawl_job(job_id)
        if job is None:
            return None
        return ChatJobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress_phase=job.progress_phase,
            started_at=job.started_at,
            ended_at=job.ended_at,
            discovered=job.discovered,
            updated=job.updated,
            failed=job.failed,
            error=job.error,
        )
