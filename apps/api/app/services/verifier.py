from __future__ import annotations

from typing import Any

from app.models.schemas import SchemeStructuredData


class VerifierService:
    def verify_against_source(
        self,
        structured_data: SchemeStructuredData,
        source_text: str,
    ) -> tuple[SchemeStructuredData, list[str]]:
        source = source_text.lower()
        data = structured_data.model_dump()
        unverified_fields: list[str] = []

        for field, value in data.items():
            if value is None:
                continue

            if isinstance(value, list):
                verified_items = [item for item in value if str(item).lower() in source]
                if not verified_items:
                    data[field] = None
                    unverified_fields.append(field)
                else:
                    data[field] = verified_items
                continue

            if isinstance(value, str):
                if value.lower() not in source:
                    data[field] = None
                    unverified_fields.append(field)

        return SchemeStructuredData.model_validate(data), unverified_fields


def diff_fields(old: dict[str, Any], new: dict[str, Any]) -> dict[str, dict[str, Any]]:
    changed: dict[str, dict[str, Any]] = {}
    for key in sorted(set(old.keys()) | set(new.keys())):
        if old.get(key) != new.get(key):
            changed[key] = {"from": old.get(key), "to": new.get(key)}
    return changed

