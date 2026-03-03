from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.factory import get_repository
from app.dependencies import (
    get_agent_orchestrator_service,
    get_anomaly_service,
    get_chat_service,
    get_embedding_service,
    get_ingestion_service,
    get_intent_classifier_service,
    get_job_orchestrator_service,
    get_retrieval_service,
)
from app.main import app
from app.models.schemas import CrawlJobRecord
from app.services.embeddings import EmbeddingService


def _reset_dependency_caches() -> None:
    os.environ["ENABLE_AGENT_ORCHESTRATION"] = "false"
    get_settings.cache_clear()
    get_repository.cache_clear()
    get_embedding_service.cache_clear()
    get_retrieval_service.cache_clear()
    get_chat_service.cache_clear()
    get_ingestion_service.cache_clear()
    get_anomaly_service.cache_clear()
    get_intent_classifier_service.cache_clear()
    get_job_orchestrator_service.cache_clear()
    get_agent_orchestrator_service.cache_clear()


def test_admin_open_source_pull_runs_ingestion_and_rebuilds_vectors(monkeypatch):
    _reset_dependency_caches()
    ingestion_service = get_ingestion_service()
    embedding_service = get_embedding_service()

    async def fake_run(**kwargs):  # type: ignore[no-untyped-def]
        now = datetime.now(timezone.utc)
        return CrawlJobRecord(
            job_id="open-source-job-1",
            started_at=now,
            ended_at=now,
            status="completed",
            progress_phase="completed",
            discovered=5,
            updated=2,
            failed=0,
            trigger_source=str(kwargs.get("trigger_source", "admin_open_source")),
            trigger_user=str(kwargs.get("trigger_user", "local-dev")),
            intent_context=str(kwargs.get("intent_context", "manual_open_source_pull")),
        )

    async def fake_reembed(provider: str | None = None) -> int:
        assert provider == "huggingface"
        return 42

    monkeypatch.setattr(ingestion_service, "run", fake_run)
    monkeypatch.setattr(embedding_service, "reembed_approved_embeddings", fake_reembed)

    with TestClient(app) as client:
        response = client.post("/api/v1/admin/crawl/run-open-source")

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "open-source-job-1"
    assert body["embedding_provider"] == "huggingface"
    assert body["vector_chunks_rebuilt"] == 42
    assert len(body["seeded_hosts"]) >= 1


def test_hf_embedding_coercion_supports_token_matrix():
    matrix = [
        [0.1, 0.3, 0.5],
        [0.3, 0.5, 0.7],
    ]
    vector = EmbeddingService._coerce_hf_embedding(matrix)
    assert len(vector) == 3
    assert vector[0] == pytest.approx(0.2)
