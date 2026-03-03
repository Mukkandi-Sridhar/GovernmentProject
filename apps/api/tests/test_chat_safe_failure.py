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


def test_chat_safe_failure_when_no_embeddings():
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

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "Am I eligible?", "language": "en", "conversation_id": "u1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["safe_failure"] is True
    assert body["answer_text"] == "I could not find official confirmation from government sources."


def test_feature_flag_false_uses_legacy_chat_service(monkeypatch):
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

    agent_orchestrator = get_agent_orchestrator_service()

    async def fail_if_called(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("Agent orchestrator must not run when feature flag is disabled")

    monkeypatch.setattr(agent_orchestrator, "answer", fail_if_called)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat/query",
            json={"query": "Am I eligible?", "language": "en", "conversation_id": "u2"},
        )

    assert response.status_code == 200
    assert response.json()["safe_failure"] is True

