from __future__ import annotations

from app.agents.state import AgentState
from app.services.chat import ChatService


class SchemeQAAgentNode:
    def __init__(self, chat_service: ChatService) -> None:
        self.chat_service = chat_service

    async def __call__(self, state: AgentState) -> AgentState:
        response = await self.chat_service.answer_scheme_qa_raw(
            query=state.get("query", ""),
            language=state.get("language", "en"),
        )
        citations = [item.model_dump(mode="json") for item in response.citations]
        return {
            **state,
            "safe_failure": response.safe_failure,
            "answer_text": response.answer_text,
            "retrieval_hits": citations,
            "citations": citations,
            "structured_cards": [item.model_dump(mode="json") for item in response.structured_cards],
            "job_id": None,
            "job_status": None,
            "action_hint": None,
        }
