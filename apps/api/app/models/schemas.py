from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class SchemeStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    flagged = "flagged"


class SchemeStructuredData(BaseModel):
    scheme_name: str | None = None
    department: str | None = None
    year: str | None = None
    eligible_castes: list[str] | None = None
    income_limit: str | None = None
    education_levels: list[str] | None = None
    special_conditions: list[str] | None = None
    required_documents: list[str] | None = None
    application_deadline: str | None = None
    application_mode: str | None = None
    official_source_url: HttpUrl | None = None


class SchemeVersionRecord(BaseModel):
    scheme_id: str
    version: int
    status: SchemeStatus
    structured_data: SchemeStructuredData
    source_url: HttpUrl
    content_hash: str
    confidence: float = Field(ge=0, le=1)
    scraped_at: datetime
    last_verified: datetime
    previous_version: int | None = None
    field_diff: dict[str, dict[str, Any]] = Field(default_factory=dict)
    canonical_text: str = ""


class EmbeddingChunkRecord(BaseModel):
    scheme_id: str
    version: int
    chunk_id: str
    chunk_text: str
    embedding_vector: list[float]
    source_url: HttpUrl
    last_updated: datetime
    status: SchemeStatus


class Citation(BaseModel):
    source_url: HttpUrl
    scheme_id: str
    version: int
    last_updated: datetime
    snippet: str


class StructuredCard(BaseModel):
    scheme_name: str
    department: str | None = None
    eligibility_summary: str | None = None
    income_limit: str | None = None
    deadline: str | None = None
    details_url: HttpUrl


class ChatQueryRequest(BaseModel):
    query: str = Field(min_length=1)
    language: str = Field(pattern="^(en|te)$")
    conversation_id: str | None = None


class ChatQueryResponse(BaseModel):
    answer_text: str
    language: str
    safe_failure: bool
    citations: list[Citation]
    structured_cards: list[StructuredCard]
    unverified_fields: list[str]
    intent: str | None = None
    job_id: str | None = None
    job_status: str | None = None
    action_hint: str | None = None


class CrawlRunResponse(BaseModel):
    job_id: str
    status: str


class CrawlJobRecord(BaseModel):
    job_id: str
    started_at: datetime
    ended_at: datetime | None = None
    status: str
    progress_phase: str = "queued"
    discovered: int = 0
    updated: int = 0
    failed: int = 0
    trigger_source: str = "admin"
    trigger_user: str = "system"
    intent_context: str | None = None
    error_code: str | None = None
    error: str | None = None


class ChatJobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_phase: str
    started_at: datetime
    ended_at: datetime | None = None
    discovered: int = 0
    updated: int = 0
    failed: int = 0
    error: str | None = None


class AuditLogRecord(BaseModel):
    scheme_id: str
    change_summary: str
    version_from: int | None
    version_to: int
    actor: str
    timestamp: datetime


class HostAllowlistRecord(BaseModel):
    host: str
    enabled: bool
    added_by: str
    added_at: datetime


class ApproveRejectRequest(BaseModel):
    reason: str = Field(min_length=3)


class HostRequest(BaseModel):
    host: str = Field(min_length=3)

