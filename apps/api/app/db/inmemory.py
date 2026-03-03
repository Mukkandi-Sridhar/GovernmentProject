from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone

from app.db.repository import Repository
from app.models.schemas import (
    AuditLogRecord,
    CrawlJobRecord,
    EmbeddingChunkRecord,
    HostAllowlistRecord,
    SchemeStatus,
    SchemeVersionRecord,
)


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self._allowlist: dict[str, HostAllowlistRecord] = {}
        self._jobs: dict[str, CrawlJobRecord] = {}
        self._versions: dict[str, list[SchemeVersionRecord]] = defaultdict(list)
        self._embeddings: list[EmbeddingChunkRecord] = []
        self._audit_logs: list[AuditLogRecord] = []
        self._conversations: list[dict[str, object]] = []
        self._lock = asyncio.Lock()

    async def list_allowlisted_hosts(self) -> list[HostAllowlistRecord]:
        async with self._lock:
            return sorted(self._allowlist.values(), key=lambda x: x.added_at, reverse=True)

    async def add_allowlisted_host(self, host: str, actor: str) -> HostAllowlistRecord:
        record = HostAllowlistRecord(
            host=host,
            enabled=True,
            added_by=actor,
            added_at=datetime.now(timezone.utc),
        )
        async with self._lock:
            self._allowlist[host] = record
        return record

    async def remove_allowlisted_host(self, host: str) -> None:
        async with self._lock:
            self._allowlist.pop(host, None)

    async def create_crawl_job(self, job: CrawlJobRecord) -> None:
        async with self._lock:
            self._jobs[job.job_id] = job

    async def update_crawl_job(self, job_id: str, **updates: object) -> None:
        async with self._lock:
            existing = self._jobs[job_id]
            self._jobs[job_id] = existing.model_copy(update=updates)

    async def list_crawl_jobs(self, limit: int = 50) -> list[CrawlJobRecord]:
        async with self._lock:
            jobs = sorted(self._jobs.values(), key=lambda x: x.started_at, reverse=True)
            return jobs[:limit]

    async def get_crawl_job(self, job_id: str) -> CrawlJobRecord | None:
        async with self._lock:
            return self._jobs.get(job_id)

    async def get_latest_version(self, scheme_id: str) -> SchemeVersionRecord | None:
        async with self._lock:
            versions = self._versions.get(scheme_id, [])
            if not versions:
                return None
            return sorted(versions, key=lambda x: x.version, reverse=True)[0]

    async def get_version(self, scheme_id: str, version: int) -> SchemeVersionRecord | None:
        async with self._lock:
            for record in self._versions.get(scheme_id, []):
                if record.version == version:
                    return record
        return None

    async def save_scheme_version(self, record: SchemeVersionRecord) -> None:
        async with self._lock:
            self._versions[record.scheme_id] = [
                version
                for version in self._versions[record.scheme_id]
                if version.version != record.version
            ]
            self._versions[record.scheme_id].append(record)

    async def list_latest_schemes(self, status: SchemeStatus | None = None) -> list[SchemeVersionRecord]:
        async with self._lock:
            latest: list[SchemeVersionRecord] = []
            for versions in self._versions.values():
                if not versions:
                    continue
                current = sorted(versions, key=lambda x: x.version, reverse=True)[0]
                if status is None or current.status == status:
                    latest.append(current)
            return sorted(latest, key=lambda x: x.last_verified, reverse=True)

    async def list_scheme_versions(self, scheme_id: str) -> list[SchemeVersionRecord]:
        async with self._lock:
            versions = self._versions.get(scheme_id, [])
            return sorted(versions, key=lambda x: x.version, reverse=True)

    async def update_scheme_status(
        self,
        scheme_id: str,
        version: int,
        status: SchemeStatus,
        actor: str,
        reason: str,
    ) -> None:
        async with self._lock:
            versions = self._versions.get(scheme_id, [])
            for idx, existing in enumerate(versions):
                if existing.version == version:
                    versions[idx] = existing.model_copy(
                        update={"status": status, "last_verified": datetime.now(timezone.utc)}
                    )
                    self._audit_logs.append(
                        AuditLogRecord(
                            scheme_id=scheme_id,
                            version_from=version,
                            version_to=version,
                            change_summary=f"Status changed to {status.value}. Reason: {reason}",
                            actor=actor,
                            timestamp=datetime.now(timezone.utc),
                        )
                    )
                    break

    async def add_audit_log(self, record: AuditLogRecord) -> None:
        async with self._lock:
            self._audit_logs.append(record)

    async def list_audit_logs(self, limit: int = 100) -> list[AuditLogRecord]:
        async with self._lock:
            logs = sorted(self._audit_logs, key=lambda x: x.timestamp, reverse=True)
            return logs[:limit]

    async def replace_embeddings_for_scheme_version(
        self,
        scheme_id: str,
        version: int,
        chunks: list[EmbeddingChunkRecord],
    ) -> None:
        async with self._lock:
            self._embeddings = [
                chunk
                for chunk in self._embeddings
                if not (chunk.scheme_id == scheme_id and chunk.version == version)
            ]
            self._embeddings.extend(chunks)

    async def list_embeddings(self, approved_only: bool = True) -> list[EmbeddingChunkRecord]:
        async with self._lock:
            if not approved_only:
                return list(self._embeddings)
            return [chunk for chunk in self._embeddings if chunk.status == SchemeStatus.approved]

    async def save_conversation_message(
        self,
        user_id: str,
        role: str,
        message: str,
        language: str,
        citations: list[dict[str, object]],
        timestamp: datetime,
    ) -> None:
        async with self._lock:
            self._conversations.append(
                {
                    "user_id": user_id,
                    "role": role,
                    "message": message,
                    "language": language,
                    "citations": citations,
                    "timestamp": timestamp,
                }
            )

