from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings
from app.db.repository import Repository
from app.dependencies import (
    get_anomaly_service,
    get_embedding_service,
    get_ingestion_service,
    get_repo_dependency,
    get_settings_dependency,
)
from app.metrics import CRAWL_RUN_COUNT
from app.models.schemas import ApproveRejectRequest, HostRequest, SchemeStatus
from app.security.auth import require_roles
from app.services.anomalies import AnomalyService
from app.services.embeddings import EmbeddingService
from app.services.ingestion import IngestionPipelineService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/crawl/run")
async def run_crawl(
    user=Depends(require_roles("admin", "reviewer")),
    ingestion_service: IngestionPipelineService = Depends(get_ingestion_service),
):
    result = await ingestion_service.run(
        actor=user["uid"],
        trigger_source="admin",
        trigger_user=user["uid"],
        intent_context="manual_admin_trigger",
    )
    CRAWL_RUN_COUNT.labels(status=result.status).inc()
    return result.model_dump(mode="json")


@router.post("/crawl/run-open-source")
async def run_open_source_pull(
    user=Depends(require_roles("admin", "reviewer")),
    repo: Repository = Depends(get_repo_dependency),
    settings: Settings = Depends(get_settings_dependency),
    ingestion_service: IngestionPipelineService = Depends(get_ingestion_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    seeded_hosts: list[str] = []
    for host in settings.open_source_seed_hosts:
        normalized = host.strip().lower()
        if not normalized:
            continue
        await repo.add_allowlisted_host(normalized, actor=user["uid"])
        seeded_hosts.append(normalized)

    result = await ingestion_service.run(
        actor=user["uid"],
        trigger_source="admin_open_source",
        trigger_user=user["uid"],
        intent_context="manual_open_source_pull",
    )
    CRAWL_RUN_COUNT.labels(status=result.status).inc()

    vector_chunks_rebuilt = await embedding_service.reembed_approved_embeddings(
        provider="huggingface",
    )
    return {
        **result.model_dump(mode="json"),
        "seeded_hosts": seeded_hosts,
        "embedding_provider": "huggingface",
        "vector_chunks_rebuilt": vector_chunks_rebuilt,
    }


@router.get("/crawl/jobs")
async def list_crawl_jobs(
    user=Depends(require_roles("admin", "reviewer")),
    repo: Repository = Depends(get_repo_dependency),
):
    rows = await repo.list_crawl_jobs()
    return [row.model_dump(mode="json") for row in rows]


@router.post("/schemes/{scheme_id}/versions/{version}/approve")
async def approve_scheme_version(
    scheme_id: str,
    version: int,
    payload: ApproveRejectRequest,
    user=Depends(require_roles("admin", "reviewer")),
    repo: Repository = Depends(get_repo_dependency),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    row = await repo.get_version(scheme_id, version)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    await repo.update_scheme_status(
        scheme_id,
        version,
        SchemeStatus.approved,
        actor=user["uid"],
        reason=payload.reason,
    )

    await embedding_service.replace_scheme_version_embeddings(
        scheme_id=scheme_id,
        version=version,
        source_url=str(row.source_url),
        text=row.canonical_text or row.structured_data.model_dump_json(),
        status=SchemeStatus.approved,
    )

    return {"ok": True, "status": "approved"}


@router.post("/schemes/{scheme_id}/versions/{version}/flag")
async def flag_scheme_version(
    scheme_id: str,
    version: int,
    payload: ApproveRejectRequest,
    user=Depends(require_roles("admin", "reviewer")),
    repo: Repository = Depends(get_repo_dependency),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    row = await repo.get_version(scheme_id, version)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    await repo.update_scheme_status(
        scheme_id,
        version,
        SchemeStatus.flagged,
        actor=user["uid"],
        reason=payload.reason,
    )

    await embedding_service.replace_scheme_version_embeddings(
        scheme_id=scheme_id,
        version=version,
        source_url=str(row.source_url),
        text=row.canonical_text or row.structured_data.model_dump_json(),
        status=SchemeStatus.flagged,
    )
    return {"ok": True, "status": "flagged"}


@router.post("/allowlist/hosts")
async def add_allowlist_host(
    payload: HostRequest,
    user=Depends(require_roles("admin")),
    repo: Repository = Depends(get_repo_dependency),
):
    row = await repo.add_allowlisted_host(payload.host.strip().lower(), actor=user["uid"])
    return row.model_dump(mode="json")


@router.delete("/allowlist/hosts/{host}")
async def remove_allowlist_host(
    host: str,
    user=Depends(require_roles("admin")),
    repo: Repository = Depends(get_repo_dependency),
):
    await repo.remove_allowlisted_host(host.strip().lower())
    return {"ok": True}


@router.get("/logs")
async def list_logs(
    user=Depends(require_roles("admin", "reviewer")),
    repo: Repository = Depends(get_repo_dependency),
):
    rows = await repo.list_audit_logs()
    return [row.model_dump(mode="json") for row in rows]


@router.get("/anomalies")
async def list_anomalies(
    user=Depends(require_roles("admin", "reviewer")),
    anomaly_service: AnomalyService = Depends(get_anomaly_service),
):
    return await anomaly_service.list_anomalies()

