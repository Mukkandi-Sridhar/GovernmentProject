from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import faiss
import httpx
import numpy as np
from google.cloud import storage
from google.oauth2 import service_account
from openai import AsyncOpenAI

from app.config import Settings
from app.db.repository import Repository
from app.logging_config import get_logger
from app.models.schemas import EmbeddingChunkRecord, SchemeStatus
from app.services.extractor import chunk_text

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self, settings: Settings, repository: Repository) -> None:
        self.settings = settings
        self.repository = repository
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.index: faiss.IndexFlatIP | None = None
        self.meta: list[dict[str, Any]] = []
        self.gcp_credentials = (
            service_account.Credentials.from_service_account_file(
                settings.google_application_credentials
            )
            if settings.google_application_credentials
            else None
        )

    async def _embed_texts(self, texts: list[str], provider: str | None = None) -> list[list[float]]:
        resolved_provider = (provider or self.settings.embedding_provider).strip().lower()
        if resolved_provider == "openai":
            return await self._embed_texts_openai(texts)
        if resolved_provider == "huggingface":
            return await self._embed_texts_huggingface(texts)
        raise RuntimeError(f"Unsupported embedding provider: {resolved_provider}")

    async def _embed_texts_openai(self, texts: list[str]) -> list[list[float]]:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings")
        response = await self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    @staticmethod
    def _is_vector(payload: object) -> bool:
        return isinstance(payload, list) and all(isinstance(item, (int, float)) for item in payload)

    @staticmethod
    def _is_token_matrix(payload: object) -> bool:
        return (
            isinstance(payload, list)
            and len(payload) > 0
            and all(isinstance(row, list) for row in payload)
            and all(
                isinstance(value, (int, float))
                for row in payload
                for value in row
            )
        )

    @classmethod
    def _coerce_hf_embedding(cls, payload: object) -> list[float]:
        if cls._is_vector(payload):
            return [float(item) for item in payload]  # type: ignore[arg-type]

        if cls._is_token_matrix(payload):
            matrix = np.array(payload, dtype="float32")
            if matrix.ndim != 2 or matrix.shape[0] == 0:
                raise RuntimeError("Invalid Hugging Face token embedding matrix")
            return matrix.mean(axis=0).astype("float32").tolist()

        if isinstance(payload, dict):
            if "error" in payload:
                raise RuntimeError(f"Hugging Face embedding error: {payload['error']}")
            if "embedding" in payload:
                return cls._coerce_hf_embedding(payload["embedding"])

        raise RuntimeError("Unexpected Hugging Face embedding response format")

    async def _embed_texts_huggingface(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        url = (
            f"{self.settings.huggingface_inference_url.rstrip('/')}/"
            f"{self.settings.huggingface_embedding_model}"
        )
        headers = {"Content-Type": "application/json"}
        if self.settings.huggingface_api_token:
            headers["Authorization"] = f"Bearer {self.settings.huggingface_api_token}"

        vectors: list[list[float]] = []
        async with httpx.AsyncClient(timeout=120) as client:
            for text in texts:
                response = await client.post(
                    url,
                    headers=headers,
                    json={"inputs": text, "options": {"wait_for_model": True}},
                )
                if response.status_code >= 400:
                    raise RuntimeError(
                        "Hugging Face inference failed "
                        f"({response.status_code}): {response.text[:300]}"
                    )
                vectors.append(self._coerce_hf_embedding(response.json()))
        return vectors

    async def create_chunks_for_scheme(
        self,
        scheme_id: str,
        version: int,
        source_url: str,
        text: str,
        status: SchemeStatus,
    ) -> list[EmbeddingChunkRecord]:
        chunks = chunk_text(text, chunk_size_tokens=800, overlap_tokens=150)
        if not chunks:
            return []

        vectors = await self._embed_texts(chunks)
        now = datetime.now(timezone.utc)
        rows = [
            EmbeddingChunkRecord(
                scheme_id=scheme_id,
                version=version,
                chunk_id=f"{scheme_id}_v{version}_{idx}",
                chunk_text=chunk,
                embedding_vector=vector,
                source_url=source_url,
                last_updated=now,
                status=status,
            )
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]
        return rows

    async def refresh_index_from_repository(self) -> int:
        rows = await self.repository.list_embeddings(approved_only=True)
        if not rows:
            self.index = None
            self.meta = []
            return 0

        matrix = np.array([row.embedding_vector for row in rows], dtype="float32")
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)

        self.index = index
        self.meta = [
            {
                "scheme_id": row.scheme_id,
                "version": row.version,
                "chunk_id": row.chunk_id,
                "chunk_text": row.chunk_text,
                "source_url": str(row.source_url),
                "last_updated": row.last_updated.isoformat(),
            }
            for row in rows
        ]
        return len(rows)

    async def query(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self.index is None:
            await self.refresh_index_from_repository()
        if self.index is None or not self.meta:
            return []

        vector = np.array((await self._embed_texts([query]))[0], dtype="float32").reshape(1, -1)
        faiss.normalize_L2(vector)
        scores, indices = self.index.search(vector, top_k)

        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx < 0 or idx >= len(self.meta):
                continue
            row = dict(self.meta[idx])
            row["score"] = float(score)
            results.append(row)
        return results

    async def save_snapshot(self) -> None:
        if self.index is None:
            return

        index_path = Path(self.settings.faiss_index_path)
        meta_path = Path(self.settings.faiss_meta_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))
        meta_path.write_text(json.dumps(self.meta), encoding="utf-8")

        if self.settings.gcs_bucket_name:
            client = storage.Client(
                project=self.settings.firebase_project_id,
                credentials=self.gcp_credentials,
            )
            bucket = client.bucket(self.settings.gcs_bucket_name)
            bucket.blob("faiss/faiss.index").upload_from_filename(str(index_path))
            bucket.blob("faiss/faiss_meta.json").upload_from_filename(str(meta_path))

    async def load_snapshot(self) -> None:
        index_path = Path(self.settings.faiss_index_path)
        meta_path = Path(self.settings.faiss_meta_path)

        if self.settings.gcs_bucket_name:
            client = storage.Client(
                project=self.settings.firebase_project_id,
                credentials=self.gcp_credentials,
            )
            bucket = client.bucket(self.settings.gcs_bucket_name)
            index_blob = bucket.blob("faiss/faiss.index")
            meta_blob = bucket.blob("faiss/faiss_meta.json")
            if index_blob.exists() and meta_blob.exists():
                index_path.parent.mkdir(parents=True, exist_ok=True)
                index_blob.download_to_filename(str(index_path))
                meta_blob.download_to_filename(str(meta_path))

        if index_path.exists() and meta_path.exists():
            self.index = faiss.read_index(str(index_path))
            self.meta = json.loads(meta_path.read_text(encoding="utf-8"))
            logger.info("Loaded FAISS snapshot with %s records", len(self.meta))

    async def replace_scheme_version_embeddings(
        self,
        scheme_id: str,
        version: int,
        source_url: str,
        text: str,
        status: SchemeStatus,
    ) -> int:
        rows = await self.create_chunks_for_scheme(scheme_id, version, source_url, text, status)
        await self.repository.replace_embeddings_for_scheme_version(scheme_id, version, rows)
        count = await self.refresh_index_from_repository()
        await self.save_snapshot()
        return count

    async def reembed_approved_embeddings(self, provider: str | None = None) -> int:
        rows = await self.repository.list_embeddings(approved_only=True)
        if not rows:
            self.index = None
            self.meta = []
            return 0

        grouped: dict[tuple[str, int, str], list[EmbeddingChunkRecord]] = {}
        for row in rows:
            key = (row.scheme_id, row.version, str(row.source_url))
            grouped.setdefault(key, []).append(row)

        for (scheme_id, version, source_url), group_rows in grouped.items():
            ordered_rows = sorted(group_rows, key=lambda row: row.chunk_id)
            vectors = await self._embed_texts(
                [row.chunk_text for row in ordered_rows],
                provider=provider,
            )
            now = datetime.now(timezone.utc)
            updated_rows = [
                EmbeddingChunkRecord(
                    scheme_id=source_row.scheme_id,
                    version=source_row.version,
                    chunk_id=source_row.chunk_id,
                    chunk_text=source_row.chunk_text,
                    embedding_vector=vector,
                    source_url=source_row.source_url,
                    last_updated=now,
                    status=source_row.status,
                )
                for source_row, vector in zip(ordered_rows, vectors, strict=True)
            ]
            await self.repository.replace_embeddings_for_scheme_version(
                scheme_id,
                version,
                updated_rows,
            )

        count = await self.refresh_index_from_repository()
        await self.save_snapshot()
        logger.info(
            "Re-embedded %s approved chunks using provider=%s",
            count,
            (provider or self.settings.embedding_provider).strip().lower(),
        )
        return count

