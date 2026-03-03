from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.nodes.collect_latest import CollectLatestDataAgentNode
from app.agents.nodes.failure import FailurePolicyNode
from app.agents.nodes.greeting import GreetingAgentNode
from app.agents.nodes.intent_router import IntentRouterNode
from app.agents.nodes.response_composer import ResponseComposerNode
from app.agents.nodes.scheme_qa import SchemeQAAgentNode
from app.agents.nodes.scope_guard import ScopeGuardAgentNode
from app.agents.state import AgentState


class AgentGraph:
    def __init__(
        self,
        intent_router_node: IntentRouterNode,
        greeting_node: GreetingAgentNode,
        scope_guard_node: ScopeGuardAgentNode,
        scheme_qa_node: SchemeQAAgentNode,
        collect_latest_node: CollectLatestDataAgentNode,
        response_composer_node: ResponseComposerNode,
        failure_node: FailurePolicyNode,
    ) -> None:
        graph = StateGraph(AgentState)

        graph.add_node("IntentRouterNode", intent_router_node)
        graph.add_node("GreetingAgentNode", greeting_node)
        graph.add_node("ScopeGuardAgentNode", scope_guard_node)
        graph.add_node("SchemeQAAgentNode", scheme_qa_node)
        graph.add_node("CollectLatestDataAgentNode", collect_latest_node)
        graph.add_node("ResponseComposerNode", response_composer_node)
        graph.add_node("FailurePolicyNode", failure_node)

        graph.set_entry_point("IntentRouterNode")

        graph.add_conditional_edges(
            "IntentRouterNode",
            self._route_after_intent,
            {
                "greeting": "GreetingAgentNode",
                "scheme_qa": "SchemeQAAgentNode",
                "collect_latest": "CollectLatestDataAgentNode",
                "out_of_scope": "ScopeGuardAgentNode",
                "ambiguous": "SchemeQAAgentNode",
            },
        )

        graph.add_edge("GreetingAgentNode", "ResponseComposerNode")
        graph.add_edge("ScopeGuardAgentNode", "ResponseComposerNode")
        graph.add_edge("SchemeQAAgentNode", "ResponseComposerNode")
        graph.add_edge("CollectLatestDataAgentNode", "ResponseComposerNode")
        graph.add_edge("FailurePolicyNode", "ResponseComposerNode")
        graph.add_edge("ResponseComposerNode", END)

        self._compiled = graph.compile()

    @staticmethod
    def _route_after_intent(state: AgentState) -> str:
        intent = state.get("intent", "ambiguous")
        if intent in {"greeting", "scheme_qa", "collect_latest", "out_of_scope", "ambiguous"}:
            return intent
        return "ambiguous"

    async def run(self, state: AgentState) -> AgentState:
        return await self._compiled.ainvoke(state)
