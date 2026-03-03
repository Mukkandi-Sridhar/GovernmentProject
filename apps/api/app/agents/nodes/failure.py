from __future__ import annotations

from app.agents.state import AgentState


class FailurePolicyNode:
    async def __call__(self, state: AgentState) -> AgentState:
        if state.get("language") == "te":
            answer = "ఇప్పుడే ఆ అభ్యర్థనను ప్రాసెస్ చేయలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి."
        else:
            answer = "I could not process that request right now. Please try again."

        return {
            **state,
            "safe_failure": True,
            "answer_text": answer,
            "retrieval_hits": [],
            "citations": [],
            "structured_cards": [],
            "job_id": None,
            "job_status": None,
            "action_hint": "Try rephrasing your question.",
            "policy_flags": (state.get("policy_flags") or []) + ["failure_policy"],
        }
