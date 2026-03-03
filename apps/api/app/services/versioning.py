from __future__ import annotations

import hashlib
import re


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "scheme"


def scheme_id_from_name_or_url(scheme_name: str | None, source_url: str) -> str:
    if scheme_name and scheme_name.strip():
        return slugify(scheme_name)
    return slugify(source_url)

