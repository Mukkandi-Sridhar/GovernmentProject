from __future__ import annotations

import json
import re

from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import Settings


@dataclass(slots=True)
class IntentResult:
    intent: str
    confidence: float
    reason: str


class IntentClassifierService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @staticmethod
    def _rule_based_classify(query: str) -> IntentResult:
        normalized = re.sub(r"\s+", " ", query.strip().lower())
        if not normalized:
            return IntentResult(intent="ambiguous", confidence=0.3, reason="Empty query")

        greeting_patterns = (
            r"\b(hi|hello|hey|namaste|good morning|good afternoon|good evening)\b",
        )
        collect_patterns = (
            r"\b(collect|refresh|reindex|ingest|crawl|latest data|update data)\b",
            r"\b(latest|newest|fresh)\b.*\b(data|updates?)\b",
        )
        scheme_patterns = (
            r"\b(scheme|scholarship|fee reimbursement|student welfare|eligib|deadline|document|apply|application)\b",
            r"\b(andhra pradesh|ap)\b.*\b(student|scheme|scholarship)\b",
        )
        out_of_scope_patterns = (
            r"\b(debug|python|java|javascript|docker|kubernetes|sql|linux)\b",
            r"\b(weather|stock|cricket|movie|recipe|travel|news)\b",
        )

        if any(re.search(pattern, normalized) for pattern in greeting_patterns) and len(normalized) <= 80:
            return IntentResult(intent="greeting", confidence=0.95, reason="Matched greeting keywords")

        if any(re.search(pattern, normalized) for pattern in collect_patterns):
            return IntentResult(intent="collect_latest", confidence=0.95, reason="Matched collection keywords")

        if any(re.search(pattern, normalized) for pattern in out_of_scope_patterns) and not any(
            re.search(pattern, normalized) for pattern in scheme_patterns
        ):
            return IntentResult(intent="out_of_scope", confidence=0.92, reason="Matched non-domain keywords")

        if any(re.search(pattern, normalized) for pattern in scheme_patterns):
            return IntentResult(intent="scheme_qa", confidence=0.88, reason="Matched scheme-domain keywords")

        return IntentResult(intent="ambiguous", confidence=0.45, reason="No clear intent pattern")

    async def classify(self, query: str) -> IntentResult:
        if not self.client:
            return self._rule_based_classify(query)

        prompt = (
            "Classify user query intent for Andhra Pradesh student welfare assistant.\n"
            "Return JSON only with keys intent, confidence, reason.\n"
            "Allowed intents: greeting, scheme_qa, collect_latest, out_of_scope, ambiguous. "
            "Intent rules:\n"
            "- greeting: user is just greeting or small talk.\n"
            "- collect_latest: explicit request to collect/refresh latest scheme data.\n"
            "- out_of_scope: request is not about Andhra Pradesh student welfare schemes.\n"
            "- scheme_qa: asks about scheme details, eligibility, deadlines, documents, official confirmation.\n"
            "- ambiguous: unclear request.\n"
            f"Query: {query}"
        )

        response = await self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a deterministic intent classifier for a civic student welfare assistant.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return self._rule_based_classify(query)

        intent = str(data.get("intent", "ambiguous"))
        if intent not in {"greeting", "scheme_qa", "collect_latest", "out_of_scope", "ambiguous"}:
            intent = "ambiguous"

        confidence_raw = data.get("confidence", 0.5)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))
        reason = str(data.get("reason", "Classifier result"))
        return IntentResult(intent=intent, confidence=confidence, reason=reason)
