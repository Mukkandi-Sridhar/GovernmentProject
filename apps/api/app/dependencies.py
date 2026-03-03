from __future__ import annotations

from functools import lru_cache

from app.config import Settings, get_settings
from app.db.factory import get_repository
from app.db.repository import Repository
from app.services.agent_orchestrator import AgentOrchestratorService
from app.services.anomalies import AnomalyService
from app.services.chat import ChatService
from app.services.classifier import ClassifierService
from app.services.crawler import CrawlerService
from app.services.embeddings import EmbeddingService
from app.services.ingestion import IngestionPipelineService
from app.services.intent_classifier import IntentClassifierService
from app.services.job_orchestrator import JobOrchestratorService
from app.services.retrieval import RetrievalService
from app.services.structurer import StructurerService
from app.services.verifier import VerifierService


@lru_cache
def get_crawler_service() -> CrawlerService:
    return CrawlerService(get_settings())


@lru_cache
def get_classifier_service() -> ClassifierService:
    return ClassifierService(get_settings())


@lru_cache
def get_structurer_service() -> StructurerService:
    return StructurerService(get_settings())


@lru_cache
def get_verifier_service() -> VerifierService:
    return VerifierService()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_settings(), get_repository())


@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(get_embedding_service())


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_settings(), get_repository(), get_retrieval_service())


@lru_cache
def get_intent_classifier_service() -> IntentClassifierService:
    return IntentClassifierService(get_settings())


@lru_cache
def get_ingestion_service() -> IngestionPipelineService:
    return IngestionPipelineService(
        get_settings(),
        get_repository(),
        get_crawler_service(),
        get_classifier_service(),
        get_structurer_service(),
        get_verifier_service(),
    )


@lru_cache
def get_job_orchestrator_service() -> JobOrchestratorService:
    return JobOrchestratorService(get_repository(), get_ingestion_service())


@lru_cache
def get_agent_orchestrator_service() -> AgentOrchestratorService:
    return AgentOrchestratorService(
        settings=get_settings(),
        repository=get_repository(),
        chat_service=get_chat_service(),
        intent_classifier=get_intent_classifier_service(),
        job_orchestrator=get_job_orchestrator_service(),
    )


@lru_cache
def get_anomaly_service() -> AnomalyService:
    return AnomalyService(get_settings(), get_repository())


def get_repo_dependency() -> Repository:
    return get_repository()


def get_settings_dependency() -> Settings:
    return get_settings()

