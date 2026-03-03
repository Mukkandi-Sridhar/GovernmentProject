from __future__ import annotations

from datetime import datetime, timezone

from app.config import Settings
from app.db.repository import Repository
from app.models.schemas import ChatQueryResponse, Citation, SchemeStatus, StructuredCard
from app.services.retrieval import RetrievalService

SAFE_FAILURE_MESSAGE = "I could not find official confirmation from government sources."


class ChatService:
    def __init__(
        self,
        settings: Settings,
        repository: Repository,
        retrieval_service: RetrievalService,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.retrieval_service = retrieval_service

    async def answer_scheme_qa_raw(self, query: str, language: str) -> ChatQueryResponse:
        retrieved = await self.retrieval_service.retrieve(query, top_k=5)
        if not retrieved:
            return ChatQueryResponse(
                answer_text=SAFE_FAILURE_MESSAGE,
                language=language,
                safe_failure=True,
                citations=[],
                structured_cards=[],
                unverified_fields=[],
                intent="scheme_qa",
            )

        citations: list[Citation] = []
        structured_cards: list[StructuredCard] = []
        seen_cards: set[tuple[str, int]] = set()
        answer_lines: list[str] = []
        evidence_count = 0

        for hit in retrieved:
            scheme_id = str(hit.get("scheme_id", ""))
            version_raw = hit.get("version")
            source_url = str(hit.get("source_url", ""))
            chunk_text = str(hit.get("chunk_text", ""))
            last_updated_raw = hit.get("last_updated")

            if not scheme_id or not source_url or not chunk_text or version_raw is None or not last_updated_raw:
                continue

            try:
                version = int(version_raw)
                last_updated = datetime.fromisoformat(str(last_updated_raw))
            except (TypeError, ValueError):
                continue
            key = (scheme_id, version)

            version_record = await self.repository.get_version(scheme_id, version)
            if version_record is None or version_record.status != SchemeStatus.approved:
                continue

            citations.append(
                Citation(
                    source_url=source_url,
                    scheme_id=scheme_id,
                    version=version,
                    last_updated=last_updated,
                    snippet=chunk_text[:320],
                )
            )
            evidence_count += 1
            answer_lines.append(
                (
                    f"{evidence_count}. scheme_id={scheme_id}; version={version}; "
                    f"last_updated={last_updated.isoformat()}; source_url={source_url}; "
                    f"official_excerpt={chunk_text[:220]}"
                )
            )

            if key not in seen_cards:
                structured_cards.append(
                    StructuredCard(
                        scheme_name=version_record.structured_data.scheme_name or scheme_id,
                        department=version_record.structured_data.department,
                        eligibility_summary=(
                            ", ".join(version_record.structured_data.education_levels or []) or None
                        ),
                        income_limit=version_record.structured_data.income_limit,
                        deadline=version_record.structured_data.application_deadline,
                        details_url=version_record.source_url,
                    )
                )
                seen_cards.add(key)

        if not citations:
            return ChatQueryResponse(
                answer_text=SAFE_FAILURE_MESSAGE,
                language=language,
                safe_failure=True,
                citations=[],
                structured_cards=[],
                unverified_fields=[],
                intent="scheme_qa",
            )

        if language == "te":
            header = "ఆమోదించిన అధికారిక మూలాల్లో లభించిన వివరాలు:"
        else:
            header = "I found the following in approved official sources:"
        answer_text = f"{header}\n" + "\n".join(answer_lines)

        return ChatQueryResponse(
            answer_text=answer_text,
            language=language,
            safe_failure=False,
            citations=citations,
            structured_cards=structured_cards,
            unverified_fields=[],
            intent="scheme_qa",
        )

    async def answer(self, user_id: str, query: str, language: str) -> ChatQueryResponse:
        response = await self.answer_scheme_qa_raw(query=query, language=language)

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
        return response
