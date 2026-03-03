from __future__ import annotations

import json
import re

from openai import AsyncOpenAI

from app.config import Settings


def _extract_json(text: str) -> dict[str, object]:
    text = text.strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


class ClassifierService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def classify_student_scheme(self, text: str, source_url: str) -> tuple[bool, float, str]:
        if not self.client:
            return False, 0.0, "OPENAI_API_KEY not configured"

        prompt = f"""
Classify whether the following official content is specifically about Andhra Pradesh student welfare schemes.
Respond only in JSON: {{"is_relevant": boolean, "confidence": number, "reason": string}}
URL: {source_url}
CONTENT:
{text[:12000]}
"""
        response = await self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a deterministic civic document classifier."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = _extract_json(content)
        is_relevant = bool(payload.get("is_relevant", False))
        confidence_raw = payload.get("confidence", 0)
        confidence = max(0.0, min(1.0, float(confidence_raw)))
        reason = str(payload.get("reason", ""))
        return is_relevant, confidence, reason

