from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.config import Settings
from app.logging_config import get_logger
from app.security.ssrf import SSRFViolation, validate_url_against_allowlist
from app.services.extractor import (
    extract_links_from_html,
    extract_sitemap_links,
    extract_text_from_html,
    extract_text_from_pdf,
)

logger = get_logger(__name__)


@dataclass(slots=True)
class CrawledDocument:
    url: str
    text: str
    content_type: str


class CrawlerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> httpx.Response | None:
        try:
            return await client.get(url, timeout=self.settings.crawl_timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed crawl fetch: %s (%s)", url, exc)
            return None

    async def crawl_host(self, host: str, allowlisted_hosts: set[str]) -> list[CrawledDocument]:
        seed_url = f"https://{host}/"
        validate_url_against_allowlist(seed_url, allowlisted_hosts, self.settings.allowed_schemes)

        headers = {"User-Agent": self.settings.crawl_user_agent}
        results: list[CrawledDocument] = []
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(seed_url, 0)])

        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            sitemap = await self._fetch(client, f"https://{host}/sitemap.xml")
            if sitemap and sitemap.status_code == 200 and "xml" in sitemap.headers.get("content-type", ""):
                for link in extract_sitemap_links(sitemap.text, host):
                    queue.append((link, 0))

            while queue and len(visited) < self.settings.crawl_max_pages_per_host:
                current_url, depth = queue.popleft()
                if current_url in visited or depth > self.settings.crawl_max_depth:
                    continue

                try:
                    validate_url_against_allowlist(current_url, allowlisted_hosts, self.settings.allowed_schemes)
                except SSRFViolation:
                    continue

                response = await self._fetch(client, current_url)
                visited.add(current_url)
                if not response or response.status_code >= 400:
                    continue

                content_type = response.headers.get("content-type", "").lower()
                parsed_host = (urlparse(current_url).hostname or "").lower()
                if parsed_host != host:
                    continue

                if "pdf" in content_type or current_url.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(response.content)
                    if text:
                        results.append(CrawledDocument(url=current_url, text=text, content_type="application/pdf"))
                    continue

                if "html" in content_type or "text" in content_type:
                    text = extract_text_from_html(response.text)
                    if text:
                        results.append(CrawledDocument(url=current_url, text=text, content_type="text/html"))

                    for link in extract_links_from_html(current_url, response.text):
                        if link not in visited:
                            queue.append((link, depth + 1))

        return results

