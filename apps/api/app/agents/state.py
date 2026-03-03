from __future__ import annotations

from typing import Any, Literal, TypedDict

AgentIntent = Literal["greeting", "scheme_qa", "collect_latest", "out_of_scope", "ambiguous"]


class AgentState(TypedDict, total=False):
    query: str
    language: str
    conversation_id: str
    intent: AgentIntent
    retrieval_hits: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    structured_cards: list[dict[str, Any]]
    job_id: str | None
    job_status: str | None
    safe_failure: bool
    answer_text: str
    policy_flags: list[str]
    action_hint: str | None
    classifier_reason: str | None
    error_message: str | None
    background_tasks: Any
    user_id: str
