from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

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
from app.models.schemas import SchemeStatus, SchemeStructuredData, SchemeVersionRecord


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


def test_pending_versions_are_not_retrieved_until_admin_approval(monkeypatch):
    _reset_dependency_caches()
    repo = get_repository()

    now = datetime.now(timezone.utc)
    version = SchemeVersionRecord(
        scheme_id="test-scheme",
        version=1,
        status=SchemeStatus.pending_review,
        structured_data=SchemeStructuredData(
            scheme_name="Test Scholarship Scheme",
            department="Education Department",
            year="2026",
            eligible_castes=["SC", "ST"],
            income_limit="Rs. 2,50,000",
            education_levels=["Degree"],
            special_conditions=["Merit-based"],
            required_documents=["Aadhaar Card"],
            application_deadline="31-08-2026",
            application_mode="Online",
            official_source_url="https://example.gov.in/scheme.pdf",
        ),
        source_url="https://example.gov.in/scheme.pdf",
        content_hash="abc123",
        confidence=0.92,
        scraped_at=now,
        last_verified=now,
        previous_version=None,
        field_diff={},
        canonical_text=(
            "Test Scholarship Scheme for Andhra Pradesh degree students. "
            "Income limit is Rs. 2,50,000 and deadline is 31-08-2026."
        ),
    )
    asyncio.run(repo.save_scheme_version(version))

    embedding_service = get_embedding_service()

    async def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [[0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77, 0.88] for _ in texts]

    monkeypatch.setattr(embedding_service, "_embed_texts", fake_embed_texts)

    with TestClient(app) as client:
        before = client.post(
            "/api/v1/chat/query",
            json={"query": "degree scholarship", "language": "en", "conversation_id": "u1"},
        )
        assert before.status_code == 200
        assert before.json()["safe_failure"] is True

        approved = client.post(
            "/api/v1/admin/schemes/test-scheme/versions/1/approve",
            json={"reason": "validated by reviewer"},
        )
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"

        after = client.post(
            "/api/v1/chat/query",
            json={"query": "degree scholarship", "language": "en", "conversation_id": "u1"},
        )
        assert after.status_code == 200
        body = after.json()
        assert body["safe_failure"] is False
        assert len(body["citations"]) > 0
        assert body["citations"][0]["scheme_id"] == "test-scheme"
