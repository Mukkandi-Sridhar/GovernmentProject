from __future__ import annotations

import json
import re

from openai import AsyncOpenAI

from app.config import Settings
from app.models.schemas import SchemeStructuredData

EXTRACTION_SYSTEM_PROMPT = """You are a deterministic government scheme extraction engine.

Extract structured data strictly from provided document content.

Return JSON:
{
  "scheme_name": "",
  "department": "",
  "year": "",
  "eligible_castes": [],
  "income_limit": "",
  "education_levels": [],
  "special_conditions": [],
  "required_documents": [],
  "application_deadline": "",
  "application_mode": "",
  "official_source_url": ""
}

Rules:
- Only extract explicitly stated data.
- If missing, return null.
- Never infer.
- Never fabricate.
- Preserve exact numeric values.
- Preserve exact dates.
"""


def _extract_json(text: str) -> dict[str, object]:
    text = text.strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


class StructurerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def extract_structured_data(self, text: str, source_url: str) -> SchemeStructuredData:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is required for structured extraction")

        response = await self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Official Source URL: {source_url}\nDocument Content:\n{text[:20000]}",
                },
            ],
        )
        payload = _extract_json(response.choices[0].message.content or "{}")
        if not payload.get("official_source_url"):
            payload["official_source_url"] = source_url
        return SchemeStructuredData.model_validate(payload)

