from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.config import Settings
from app.db.repository import Repository
from app.logging_config import get_logger
from app.models.schemas import AuditLogRecord, CrawlJobRecord, SchemeStatus, SchemeVersionRecord
from app.services.classifier import ClassifierService
from app.services.crawler import CrawlerService
from app.services.structurer import StructurerService
from app.services.verifier import VerifierService, diff_fields
from app.services.versioning import compute_content_hash, scheme_id_from_name_or_url

logger = get_logger(__name__)


class IngestionPipelineService:
    def __init__(
        self,
        settings: Settings,
        repository: Repository,
        crawler_service: CrawlerService,
        classifier_service: ClassifierService,
        structurer_service: StructurerService,
        verifier_service: VerifierService,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.crawler_service = crawler_service
        self.classifier_service = classifier_service
        self.structurer_service = structurer_service
        self.verifier_service = verifier_service

    async def _update_job_progress(
        self,
        job_id: str,
        progress_phase: str,
        discovered: int,
        updated: int,
        failed: int,
    ) -> None:
        await self.repository.update_crawl_job(
            job_id,
            status="running",
            progress_phase=progress_phase,
            discovered=discovered,
            updated=updated,
            failed=failed,
        )

    async def run(
        self,
        actor: str = "system",
        trigger_source: str = "admin",
        trigger_user: str | None = None,
        intent_context: str | None = None,
        job_id: str | None = None,
    ) -> CrawlJobRecord:
        started_at = datetime.now(timezone.utc)
        resolved_job_id = job_id or str(uuid4())
        job = CrawlJobRecord(
            job_id=resolved_job_id,
            started_at=started_at,
            status="running",
            progress_phase="running",
            trigger_source=trigger_source,
            trigger_user=trigger_user or actor,
            intent_context=intent_context,
        )
        existing = await self.repository.get_crawl_job(resolved_job_id)
        if existing:
            await self.repository.update_crawl_job(
                resolved_job_id,
                status="running",
                progress_phase="running",
                trigger_source=trigger_source,
                trigger_user=trigger_user or actor,
                intent_context=intent_context,
                error=None,
                error_code=None,
            )
        else:
            await self.repository.create_crawl_job(job)

        discovered = 0
        updated = 0
        failed = 0

        hosts = [record.host for record in await self.repository.list_allowlisted_hosts() if record.enabled]
        allowlisted = set(hosts)

        if not hosts:
            await self.repository.update_crawl_job(
                resolved_job_id,
                status="completed",
                progress_phase="completed",
                discovered=0,
                updated=0,
                failed=0,
                ended_at=datetime.now(timezone.utc),
            )
            return CrawlJobRecord(
                **job.model_dump(mode="python"),
                status="completed",
                progress_phase="completed",
                ended_at=datetime.now(timezone.utc),
            )

        for host in hosts:
            await self._update_job_progress(
                resolved_job_id,
                progress_phase=f"crawling:{host}",
                discovered=discovered,
                updated=updated,
                failed=failed,
            )
            try:
                docs = await self.crawler_service.crawl_host(host, allowlisted)
            except Exception as exc:  # noqa: BLE001
                logger.error("Host crawl failed for %s: %s", host, exc)
                failed += 1
                await self._update_job_progress(
                    resolved_job_id,
                    progress_phase=f"host_failed:{host}",
                    discovered=discovered,
                    updated=updated,
                    failed=failed,
                )
                continue

            discovered += len(docs)
            await self._update_job_progress(
                resolved_job_id,
                progress_phase=f"processing:{host}:0/{len(docs)}",
                discovered=discovered,
                updated=updated,
                failed=failed,
            )
            for index, doc in enumerate(docs, start=1):
                try:
                    is_relevant, confidence, _ = await self.classifier_service.classify_student_scheme(
                        doc.text,
                        doc.url,
                    )
                    if not is_relevant:
                        continue

                    structured = await self.structurer_service.extract_structured_data(doc.text, doc.url)
                    verified, unverified_fields = self.verifier_service.verify_against_source(
                        structured,
                        doc.text,
                    )

                    scheme_id = scheme_id_from_name_or_url(verified.scheme_name, doc.url)
                    content_hash = compute_content_hash(doc.text)
                    latest = await self.repository.get_latest_version(scheme_id)
                    if latest and latest.content_hash == content_hash:
                        continue

                    version = 1 if latest is None else latest.version + 1
                    previous_version = latest.version if latest else None
                    field_diff = (
                        diff_fields(
                            latest.structured_data.model_dump() if latest else {},
                            verified.model_dump(),
                        )
                        if latest
                        else {}
                    )

                    record = SchemeVersionRecord(
                        scheme_id=scheme_id,
                        version=version,
                        status=SchemeStatus.pending_review,
                        structured_data=verified,
                        source_url=doc.url,
                        content_hash=content_hash,
                        confidence=confidence,
                        scraped_at=datetime.now(timezone.utc),
                        last_verified=datetime.now(timezone.utc),
                        previous_version=previous_version,
                        field_diff=field_diff,
                        canonical_text=doc.text,
                    )
                    await self.repository.save_scheme_version(record)
                    await self.repository.add_audit_log(
                        AuditLogRecord(
                            scheme_id=scheme_id,
                            version_from=previous_version,
                            version_to=version,
                            change_summary=(
                                f"Created version {version}. Unverified fields nullified: "
                                f"{', '.join(unverified_fields) if unverified_fields else 'none'}"
                            ),
                            actor=actor,
                            timestamp=datetime.now(timezone.utc),
                        )
                    )
                    updated += 1
                except Exception as exc:  # noqa: BLE001
                    logger.error("Document processing failed for %s: %s", doc.url, exc)
                    failed += 1

                if index % 5 == 0 or index == len(docs):
                    await self._update_job_progress(
                        resolved_job_id,
                        progress_phase=f"processing:{host}:{index}/{len(docs)}",
                        discovered=discovered,
                        updated=updated,
                        failed=failed,
                    )

        ended = datetime.now(timezone.utc)
        await self.repository.update_crawl_job(
            resolved_job_id,
            status="completed",
            progress_phase="completed",
            discovered=discovered,
            updated=updated,
            failed=failed,
            ended_at=ended,
        )
        return CrawlJobRecord(
            job_id=resolved_job_id,
            started_at=started_at,
            ended_at=ended,
            status="completed",
            progress_phase="completed",
            discovered=discovered,
            updated=updated,
            failed=failed,
            trigger_source=trigger_source,
            trigger_user=trigger_user or actor,
            intent_context=intent_context,
        )

