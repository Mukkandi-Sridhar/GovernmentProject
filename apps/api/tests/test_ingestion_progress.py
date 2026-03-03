from __future__ import annotations

import pytest

from app.config import Settings
from app.db.inmemory import InMemoryRepository
from app.models.schemas import SchemeStructuredData
from app.services.ingestion import IngestionPipelineService


class _FakeCrawler:
    async def crawl_host(self, host: str, allowlisted_hosts: set[str]):  # type: ignore[no-untyped-def]
        class _Doc:
            def __init__(self, url: str, text: str) -> None:
                self.url = url
                self.text = text

        return [
            _Doc(f"https://{host}/scheme-1", "Scholarship One income limit 100000"),
            _Doc(f"https://{host}/scheme-2", "Scholarship Two income limit 200000"),
        ]


class _FakeClassifier:
    async def classify_student_scheme(self, text: str, source_url: str):  # type: ignore[no-untyped-def]
        return True, 0.95, "matched"


class _FakeStructurer:
    async def extract_structured_data(self, text: str, source_url: str) -> SchemeStructuredData:
        return SchemeStructuredData(
            scheme_name="Test Scholarship",
            income_limit="100000",
            official_source_url=source_url,
        )


class _FakeVerifier:
    def verify_against_source(self, structured_data: SchemeStructuredData, source_text: str):  # type: ignore[no-untyped-def]
        return structured_data, []


@pytest.mark.asyncio
async def test_ingestion_updates_progress_phase_during_run(monkeypatch: pytest.MonkeyPatch):
    repository = InMemoryRepository()
    await repository.add_allowlisted_host("ap.gov.in", actor="tester")
    settings = Settings(openai_api_key=None)

    service = IngestionPipelineService(
        settings=settings,
        repository=repository,
        crawler_service=_FakeCrawler(),  # type: ignore[arg-type]
        classifier_service=_FakeClassifier(),  # type: ignore[arg-type]
        structurer_service=_FakeStructurer(),  # type: ignore[arg-type]
        verifier_service=_FakeVerifier(),  # type: ignore[arg-type]
    )

    progress_phases: list[str] = []
    original_update = repository.update_crawl_job

    async def tracked_update(job_id: str, **updates: object) -> None:
        phase = updates.get("progress_phase")
        if isinstance(phase, str):
            progress_phases.append(phase)
        await original_update(job_id, **updates)

    monkeypatch.setattr(repository, "update_crawl_job", tracked_update)

    result = await service.run(actor="tester", trigger_source="admin", trigger_user="tester")

    assert result.status == "completed"
    assert any(phase.startswith("crawling:") for phase in progress_phases)
    assert any(phase.startswith("processing:") for phase in progress_phases)
    assert progress_phases[-1] == "completed"
