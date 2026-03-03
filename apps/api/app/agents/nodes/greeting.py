from __future__ import annotations

from app.agents.state import AgentState


class GreetingAgentNode:
    async def __call__(self, state: AgentState) -> AgentState:
        if state.get("language") == "te":
            answer = (
                "నమస్కారం. నేను ఆంధ్రప్రదేశ్ విద్యార్థి సంక్షేమ సహాయకుడిని. "
                "పథకాల అర్హత, గడువు తేదీలు, లేదా అధికారిక మూలాల గురించి అడగండి."
            )
        else:
            answer = (
                "Hello. I am the Andhra Pradesh student welfare assistant. "
                "Ask me about scheme eligibility, deadlines, or official sources."
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
            "action_hint": "Ask a specific scheme question for official details.",
        }
