from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.schemas import (
    AuditLogRecord,
    CrawlJobRecord,
    EmbeddingChunkRecord,
    HostAllowlistRecord,
    SchemeStatus,
    SchemeVersionRecord,
)


class Repository(ABC):
    @abstractmethod
    async def list_allowlisted_hosts(self) -> list[HostAllowlistRecord]:
        raise NotImplementedError

    @abstractmethod
    async def add_allowlisted_host(self, host: str, actor: str) -> HostAllowlistRecord:
        raise NotImplementedError

    @abstractmethod
    async def remove_allowlisted_host(self, host: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_crawl_job(self, job: CrawlJobRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_crawl_job(self, job_id: str, **updates: object) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_crawl_jobs(self, limit: int = 50) -> list[CrawlJobRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_crawl_job(self, job_id: str) -> CrawlJobRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_latest_version(self, scheme_id: str) -> SchemeVersionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_version(self, scheme_id: str, version: int) -> SchemeVersionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def save_scheme_version(self, record: SchemeVersionRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_latest_schemes(self, status: SchemeStatus | None = None) -> list[SchemeVersionRecord]:
        raise NotImplementedError

    @abstractmethod
    async def list_scheme_versions(self, scheme_id: str) -> list[SchemeVersionRecord]:
        raise NotImplementedError

    @abstractmethod
    async def update_scheme_status(
        self,
        scheme_id: str,
        version: int,
        status: SchemeStatus,
        actor: str,
        reason: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_audit_log(self, record: AuditLogRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_audit_logs(self, limit: int = 100) -> list[AuditLogRecord]:
        raise NotImplementedError

    @abstractmethod
    async def replace_embeddings_for_scheme_version(
        self,
        scheme_id: str,
        version: int,
        chunks: list[EmbeddingChunkRecord],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_embeddings(self, approved_only: bool = True) -> list[EmbeddingChunkRecord]:
        raise NotImplementedError

    @abstractmethod
    async def save_conversation_message(
        self,
        user_id: str,
        role: str,
        message: str,
        language: str,
        citations: list[dict[str, object]],
        timestamp: datetime,
    ) -> None:
        raise NotImplementedError

