from __future__ import annotations

from datetime import datetime, timezone

from fastapi import BackgroundTasks

from app.agents.graph import AgentGraph
from app.agents.nodes.collect_latest import CollectLatestDataAgentNode
from app.agents.nodes.failure import FailurePolicyNode
from app.agents.nodes.greeting import GreetingAgentNode
from app.agents.nodes.intent_router import IntentRouterNode
from app.agents.nodes.response_composer import ResponseComposerNode
from app.agents.nodes.scheme_qa import SchemeQAAgentNode
from app.agents.nodes.scope_guard import ScopeGuardAgentNode
from app.agents.state import AgentState
from app.config import Settings
from app.db.repository import Repository
from app.models.schemas import ChatQueryResponse, Citation, StructuredCard
from app.services.chat import ChatService
from app.services.intent_classifier import IntentClassifierService
from app.services.job_orchestrator import JobOrchestratorService

SAFE_FAILURE_MESSAGE = "I could not find official confirmation from government sources."


class AgentOrchestratorService:
    def __init__(
        self,
        settings: Settings,
        repository: Repository,
        chat_service: ChatService,
        intent_classifier: IntentClassifierService,
        job_orchestrator: JobOrchestratorService,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.chat_service = chat_service
        self.intent_classifier = intent_classifier
        self.job_orchestrator = job_orchestrator

        self.failure_node = FailurePolicyNode()
        self.graph = AgentGraph(
            intent_router_node=IntentRouterNode(self.intent_classifier),
            greeting_node=GreetingAgentNode(),
            scope_guard_node=ScopeGuardAgentNode(),
            scheme_qa_node=SchemeQAAgentNode(self.chat_service),
            collect_latest_node=CollectLatestDataAgentNode(self.job_orchestrator),
            response_composer_node=ResponseComposerNode(),
            failure_node=self.failure_node,
        )

    async def _persist_chat_turn(
        self,
        user_id: str,
        query: str,
        language: str,
        response: ChatQueryResponse,
    ) -> None:
        now = datetime.now(timezone.utc)
        await self.repository.save_conversation_message(user_id, "user", query, language, [], now)
        await self.repository.save_conversation_message(
            user_id,
            "assistant",
            response.answer_text,
            language,
            [citation.model_dump(mode="json") for citation in response.citations],
            now,
        )

    @staticmethod
    def _to_response(state: AgentState, language: str) -> ChatQueryResponse:
        citations = [Citation.model_validate(item) for item in state.get("citations", [])]
        cards = [StructuredCard.model_validate(item) for item in state.get("structured_cards", [])]

        answer_text = state.get("answer_text") or SAFE_FAILURE_MESSAGE
        safe_failure = bool(state.get("safe_failure", False))

        return ChatQueryResponse(
            answer_text=answer_text,
            language=language,
            safe_failure=safe_failure,
            citations=citations,
            structured_cards=cards,
            unverified_fields=[],
            intent=state.get("intent"),
            job_id=state.get("job_id"),
            job_status=state.get("job_status"),
            action_hint=state.get("action_hint"),
        )

    async def answer(
        self,
        user_id: str,
        query: str,
        language: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> ChatQueryResponse:


        state: AgentState = {
            "query": query,
            "language": language,
            "conversation_id": user_id,
            "user_id": user_id,
            "intent": "ambiguous",
            "retrieval_hits": [],
            "citations": [],
            "structured_cards": [],
            "job_id": None,
            "job_status": None,
            "safe_failure": False,
            "answer_text": "",
            "policy_flags": [],
            "background_tasks": background_tasks,
        }

        try:
            result_state = await self.graph.run(state)
        except Exception as exc:  # noqa: BLE001
            result_state = await self.failure_node(
                {
                    **state,
                    "error_message": str(exc),
                }
            )

        response = self._to_response(result_state, language)
        await self._persist_chat_turn(user_id, query, language, response)
        return response
