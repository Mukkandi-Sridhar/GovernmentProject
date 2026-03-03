from __future__ import annotations

from app.agents.state import AgentState


class ResponseComposerNode:
    async def __call__(self, state: AgentState) -> AgentState:
        return {
            **state,
            "safe_failure": bool(state.get("safe_failure", False)),
            "answer_text": state.get("answer_text", ""),
            "retrieval_hits": list(state.get("retrieval_hits", [])),
            "citations": list(state.get("citations", [])),
            "structured_cards": list(state.get("structured_cards", [])),
            "job_id": state.get("job_id"),
            "job_status": state.get("job_status"),
            "action_hint": state.get("action_hint"),
            "policy_flags": list(state.get("policy_flags", [])),
        }
