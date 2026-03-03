from __future__ import annotations

import os

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


def _reset(enable_orchestration: bool = True) -> None:
    os.environ["ENABLE_AGENT_ORCHESTRATION"] = "true" if enable_orchestration else "false"
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


def test_greeting_routed_to_smalltalk_agent():
    _reset(True)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "hello", "language": "en", "conversation_id": "u-greet"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "greeting"
    assert body["safe_failure"] is False
    assert body["citations"] == []


def test_out_of_scope_question_hits_scope_guard_agent():
    _reset(True)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "how to debug a python api", "language": "en", "conversation_id": "u-scope"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "out_of_scope"
    assert body["safe_failure"] is False
    assert "only help with Andhra Pradesh student welfare schemes" in body["answer_text"]


def test_collect_latest_creates_job_and_status_endpoint_works():
    _reset(True)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "collect latest data", "language": "en", "conversation_id": "u-collect"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "collect_latest"
    assert body["job_id"] is not None
    assert body["job_status"] in {"queued", "running", "completed", "failed"}

    status_response = client.get(f"/api/v1/chat/jobs/{body['job_id']}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["job_id"] == body["job_id"]
    assert status_body["status"] in {"queued", "running", "completed", "failed"}


def test_scheme_qa_still_returns_safe_failure_without_evidence():
    _reset(True)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "What is the eligibility for degree scholarship?", "language": "en", "conversation_id": "u-scheme"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "scheme_qa"
    assert body["safe_failure"] is True
    assert body["answer_text"] == "I could not find official confirmation from government sources."


def test_ambiguous_intent_falls_back_to_scheme_qa():
    _reset(True)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "details please", "language": "en", "conversation_id": "u-ambiguous"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "scheme_qa"
    assert body["safe_failure"] is True
    assert body["answer_text"] == "I could not find official confirmation from government sources."


def test_greeting_and_out_of_scope_do_not_trigger_retrieval(monkeypatch):
    _reset(True)
    retrieval_service = get_retrieval_service()
    calls = {"count": 0}

    async def tracked_retrieve(query: str, top_k: int = 5) -> list[dict[str, object]]:
        calls["count"] += 1
        return []

    monkeypatch.setattr(retrieval_service, "retrieve", tracked_retrieve)

    with TestClient(app) as client:
        greeting = client.post(
            "/api/v1/chat/query",
            json={"query": "hello", "language": "en", "conversation_id": "u-no-retrieval-1"},
        )
        assert greeting.status_code == 200
        assert greeting.json()["intent"] == "greeting"

        out_of_scope = client.post(
            "/api/v1/chat/query",
            json={
                "query": "how to debug python api",
                "language": "en",
                "conversation_id": "u-no-retrieval-2",
            },
        )
        assert out_of_scope.status_code == 200
        assert out_of_scope.json()["intent"] == "out_of_scope"

    assert calls["count"] == 0
