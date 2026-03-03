from __future__ import annotations

from datetime import datetime, timezone

from app.config import Settings
from app.db.repository import Repository
from app.models.schemas import SchemeStatus


class AnomalyService:
    def __init__(self, settings: Settings, repository: Repository) -> None:
        self.settings = settings
        self.repository = repository

    async def list_anomalies(self) -> list[dict[str, object]]:
        rows = await self.repository.list_latest_schemes()
        now = datetime.now(timezone.utc)
        anomalies: list[dict[str, object]] = []

        for row in rows:
            age_hours = (now - row.last_verified).total_seconds() / 3600
            if row.confidence < 0.55:
                anomalies.append(
                    {
                        "type": "low_confidence",
                        "scheme_id": row.scheme_id,
                        "version": row.version,
                        "confidence": row.confidence,
                    }
                )
            if age_hours > self.settings.stale_data_hours:
                anomalies.append(
                    {
                        "type": "stale_data",
                        "scheme_id": row.scheme_id,
                        "version": row.version,
                        "hours_old": int(age_hours),
                    }
                )
            if row.status == SchemeStatus.flagged:
                anomalies.append(
                    {
                        "type": "flagged",
                        "scheme_id": row.scheme_id,
                        "version": row.version,
                    }
                )

        return anomalies

