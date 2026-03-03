from __future__ import annotations

from app.agents.state import AgentState


class ScopeGuardAgentNode:
    async def __call__(self, state: AgentState) -> AgentState:
        if state.get("language") == "te":
            answer = (
                "క్షమించండి, నేను ఆంధ్రప్రదేశ్ విద్యార్థి సంక్షేమ పథకాల గురించి మాత్రమే సహాయం చేయగలను. "
                "దయచేసి అర్హత, గడువు తేదీలు, అవసరమైన పత్రాలు, లేదా అధికారిక మూలాల గురించి అడగండి."
            )
        else:
            answer = (
                "I can only help with Andhra Pradesh student welfare schemes. "
                "Please ask about scheme eligibility, deadlines, required documents, or official sources."
            )

        return {
            **state,
            "safe_failure": False,
            "answer_text": answer,
            "retrieval_hits": [],
            "citations": [],
            "structured_cards": [],
            "job_id": None,
            "job_status": None,
            "action_hint": "Try a scheme-focused query.",
        }
