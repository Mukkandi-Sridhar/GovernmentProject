from __future__ import annotations

from app.services.embeddings import EmbeddingService


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        return await self.embedding_service.query(query=query, top_k=top_k)

