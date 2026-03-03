from __future__ import annotations

from app.agents.state import AgentState
from app.services.intent_classifier import IntentClassifierService


class IntentRouterNode:
    def __init__(self, intent_classifier: IntentClassifierService) -> None:
        self.intent_classifier = intent_classifier

    async def __call__(self, state: AgentState) -> AgentState:
        result = await self.intent_classifier.classify(state.get("query", ""))
        intent = result.intent
        policy_flags = list(state.get("policy_flags", []))
        if result.intent == "ambiguous":
            intent = "scheme_qa"
            policy_flags.append("ambiguous_to_scheme_qa")

        return {
            **state,
            "intent": intent,
            "classifier_reason": result.reason,
            "policy_flags": policy_flags,
        }
