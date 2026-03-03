from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from google.cloud import firestore
from google.oauth2 import service_account

from app.db.repository import Repository
from app.models.schemas import (
    AuditLogRecord,
    CrawlJobRecord,
    EmbeddingChunkRecord,
    HostAllowlistRecord,
    SchemeStatus,
    SchemeVersionRecord,
)


class FirestoreRepository(Repository):
    def __init__(
        self,
        project_id: str | None = None,
        credentials_path: str | None = None,
    ) -> None:
        credentials = None
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
        self.client = firestore.AsyncClient(project=project_id, credentials=credentials)

    async def list_allowlisted_hosts(self) -> list[HostAllowlistRecord]:
        docs = self.client.collection("host_allowlist").where("enabled", "==", True).stream()
        records: list[HostAllowlistRecord] = []
        async for doc in docs:
            records.append(HostAllowlistRecord(**doc.to_dict()))
        return sorted(records, key=lambda x: x.added_at, reverse=True)

    async def add_allowlisted_host(self, host: str, actor: str) -> HostAllowlistRecord:
        record = HostAllowlistRecord(
            host=host,
            enabled=True,
            added_by=actor,
            added_at=datetime.now(timezone.utc),
        )
        await self.client.collection("host_allowlist").document(host).set(record.model_dump(mode="json"))
        return record

    async def remove_allowlisted_host(self, host: str) -> None:
        await self.client.collection("host_allowlist").document(host).delete()

    async def create_crawl_job(self, job: CrawlJobRecord) -> None:
        await self.client.collection("crawl_jobs").document(job.job_id).set(job.model_dump(mode="json"))

    async def update_crawl_job(self, job_id: str, **updates: object) -> None:
        await self.client.collection("crawl_jobs").document(job_id).set(updates, merge=True)

    async def list_crawl_jobs(self, limit: int = 50) -> list[CrawlJobRecord]:
        query = (
            self.client.collection("crawl_jobs")
            .order_by("started_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        rows: list[CrawlJobRecord] = []
        async for doc in query:
            rows.append(CrawlJobRecord(**doc.to_dict()))
        return rows

    async def get_crawl_job(self, job_id: str) -> CrawlJobRecord | None:
        doc = await self.client.collection("crawl_jobs").document(job_id).get()
        if not doc.exists:
            return None
        return CrawlJobRecord(**doc.to_dict())

    async def get_latest_version(self, scheme_id: str) -> SchemeVersionRecord | None:
        query = (
            self.client.collection("schemes")
            .where("scheme_id", "==", scheme_id)
            .order_by("version", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        async for doc in query:
            return SchemeVersionRecord(**doc.to_dict())
        return None

    async def get_version(self, scheme_id: str, version: int) -> SchemeVersionRecord | None:
        doc_id = f"{scheme_id}_v{version}"
        doc = await self.client.collection("schemes").document(doc_id).get()
        if not doc.exists:
            return None
        return SchemeVersionRecord(**doc.to_dict())

    async def save_scheme_version(self, record: SchemeVersionRecord) -> None:
        doc_id = f"{record.scheme_id}_v{record.version}"
        await self.client.collection("schemes").document(doc_id).set(record.model_dump(mode="json"))

    async def list_latest_schemes(self, status: SchemeStatus | None = None) -> list[SchemeVersionRecord]:
        stream = self.client.collection("schemes").stream()
        grouped: dict[str, SchemeVersionRecord] = {}
        async for doc in stream:
            row = SchemeVersionRecord(**doc.to_dict())
            if status and row.status != status:
                continue
            existing = grouped.get(row.scheme_id)
            if existing is None or row.version > existing.version:
                grouped[row.scheme_id] = row
        return sorted(grouped.values(), key=lambda x: x.last_verified, reverse=True)

    async def list_scheme_versions(self, scheme_id: str) -> list[SchemeVersionRecord]:
        query = (
            self.client.collection("schemes")
            .where("scheme_id", "==", scheme_id)
            .order_by("version", direction=firestore.Query.DESCENDING)
            .stream()
        )
        rows: list[SchemeVersionRecord] = []
        async for doc in query:
            rows.append(SchemeVersionRecord(**doc.to_dict()))
        return rows

    async def update_scheme_status(
        self,
        scheme_id: str,
        version: int,
        status: SchemeStatus,
        actor: str,
        reason: str,
    ) -> None:
        doc_id = f"{scheme_id}_v{version}"
        await self.client.collection("schemes").document(doc_id).set(
            {
                "status": status.value,
                "last_verified": datetime.now(timezone.utc).isoformat(),
            },
            merge=True,
        )
        await self.add_audit_log(
            AuditLogRecord(
                scheme_id=scheme_id,
                version_from=version,
                version_to=version,
                change_summary=f"Status changed to {status.value}. Reason: {reason}",
                actor=actor,
                timestamp=datetime.now(timezone.utc),
            )
        )

    async def add_audit_log(self, record: AuditLogRecord) -> None:
        await self.client.collection("audit_logs").add(record.model_dump(mode="json"))

    async def list_audit_logs(self, limit: int = 100) -> list[AuditLogRecord]:
        stream = (
            self.client.collection("audit_logs")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        rows: list[AuditLogRecord] = []
        async for doc in stream:
            rows.append(AuditLogRecord(**doc.to_dict()))
        return rows

    async def replace_embeddings_for_scheme_version(
        self,
        scheme_id: str,
        version: int,
        chunks: list[EmbeddingChunkRecord],
    ) -> None:
        existing = (
            self.client.collection("embeddings")
            .where("scheme_id", "==", scheme_id)
            .where("version", "==", version)
            .stream()
        )
        delete_tasks = []
        async for doc in existing:
            delete_tasks.append(doc.reference.delete())
        if delete_tasks:
            await asyncio.gather(*delete_tasks)

        write_tasks = []
        for chunk in chunks:
            write_tasks.append(self.client.collection("embeddings").add(chunk.model_dump(mode="json")))
        if write_tasks:
            await asyncio.gather(*write_tasks)

    async def list_embeddings(self, approved_only: bool = True) -> list[EmbeddingChunkRecord]:
        stream = self.client.collection("embeddings").stream()
        rows: list[EmbeddingChunkRecord] = []
        async for doc in stream:
            row = EmbeddingChunkRecord(**doc.to_dict())
            if approved_only and row.status != SchemeStatus.approved:
                continue
            rows.append(row)
        return rows

    async def save_conversation_message(
        self,
        user_id: str,
        role: str,
        message: str,
        language: str,
        citations: list[dict[str, object]],
        timestamp: datetime,
    ) -> None:
        await self.client.collection("conversations").add(
            {
                "user_id": user_id,
                "role": role,
                "message": message,
                "language": language,
                "citations": citations,
                "timestamp": timestamp.isoformat(),
            }
        )

