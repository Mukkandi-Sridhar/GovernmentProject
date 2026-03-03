from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from app.config import Settings
from app.db.repository import Repository
from app.dependencies import (
    get_agent_orchestrator_service,
    get_chat_service,
    get_job_orchestrator_service,
    get_repo_dependency,
    get_settings_dependency,
)
from app.models.schemas import (
    ChatJobStatusResponse,
    ChatQueryRequest,
    ChatQueryResponse,
    SchemeStatus,
)
from app.services.agent_orchestrator import AgentOrchestratorService
from app.services.chat import ChatService
from app.services.job_orchestrator import JobOrchestratorService

router = APIRouter(prefix="/api/v1", tags=["public"])


@router.post("/chat/query", response_model=ChatQueryResponse)
async def chat_query(
    payload: ChatQueryRequest,
    background_tasks: BackgroundTasks,
    agent_orchestrator: AgentOrchestratorService = Depends(get_agent_orchestrator_service),
    chat_service: ChatService = Depends(get_chat_service),
    settings: Settings = Depends(get_settings_dependency),
) -> ChatQueryResponse:
    user_id = payload.conversation_id or "anonymous"
    if not settings.enable_agent_orchestration:
        return await chat_service.answer(
            user_id=user_id,
            query=payload.query,
            language=payload.language,
        )

    return await agent_orchestrator.answer(
        user_id=user_id,
        query=payload.query,
        language=payload.language,
        background_tasks=background_tasks,
    )


@router.get("/chat/jobs/{job_id}", response_model=ChatJobStatusResponse)
async def chat_job_status(
    job_id: str,
    job_orchestrator: JobOrchestratorService = Depends(get_job_orchestrator_service),
) -> ChatJobStatusResponse:
    row = await job_orchestrator.get_job_status(job_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return row


@router.get("/schemes")
async def list_schemes(
    status_filter: SchemeStatus = Query(default=SchemeStatus.approved, alias="status"),
    repo: Repository = Depends(get_repo_dependency),
):
    rows = await repo.list_latest_schemes(status=status_filter)
    return [row.model_dump(mode="json") for row in rows]


@router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, repo: Repository = Depends(get_repo_dependency)):
    row = await repo.get_latest_version(scheme_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found")
    return row.model_dump(mode="json")


@router.get("/schemes/{scheme_id}/versions")
async def get_scheme_versions(scheme_id: str, repo: Repository = Depends(get_repo_dependency)):
    rows = await repo.list_scheme_versions(scheme_id)
    return [row.model_dump(mode="json") for row in rows]


@router.get("/schemes/{scheme_id}/versions/{version}/diff")
async def get_scheme_diff(scheme_id: str, version: int, repo: Repository = Depends(get_repo_dependency)):
    row = await repo.get_version(scheme_id, version)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return {
        "scheme_id": scheme_id,
        "version": version,
        "field_diff": row.field_diff,
        "previous_version": row.previous_version,
    }

