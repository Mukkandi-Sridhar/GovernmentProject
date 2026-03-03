from __future__ import annotations

from app.agents.state import AgentState
from app.services.job_orchestrator import JobOrchestratorService


class CollectLatestDataAgentNode:
    def __init__(self, job_orchestrator: JobOrchestratorService) -> None:
        self.job_orchestrator = job_orchestrator

    async def __call__(self, state: AgentState) -> AgentState:
        user_id = state.get("user_id", "anonymous")
        intent_context = state.get("query", "collect latest data")
        background_tasks = state.get("background_tasks")

        job = await self.job_orchestrator.trigger_collection_from_chat(
            user_id=user_id,
            intent_context=intent_context,
            background_tasks=background_tasks,
        )

        if state.get("language") == "te":
            answer_text = (
                "తాజా డేటా సేకరణ ప్రారంభించాం. "
                f"జాబ్ ఐడి: {job.job_id}. కొద్దిసేపటికి స్థితి చూడండి."
            )
            action_hint = "ప్రగతి కోసం chat/jobs/{job_id} చూడండి."
        else:
            answer_text = (
                "Latest data collection has started. "
                f"Job ID: {job.job_id}. Please check status shortly."
            )
            action_hint = "Use chat/jobs/{job_id} to check progress."

        return {
            **state,
            "safe_failure": False,
            "answer_text": answer_text,
            "retrieval_hits": [],
            "citations": [],
            "structured_cards": [],
            "job_id": job.job_id,
            "job_status": job.status,
            "action_hint": action_hint,
        }
