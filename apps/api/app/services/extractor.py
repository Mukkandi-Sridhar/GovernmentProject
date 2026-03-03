from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from urllib.parse import urljoin, urlparse

import pdfplumber
from bs4 import BeautifulSoup


@dataclass(slots=True)
class NormalizedDocument:
    url: str
    text: str
    content_type: str


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return normalize_text(soup.get_text(" "))


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    texts: list[str] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return normalize_text("\n".join(texts))


def extract_links_from_html(base_url: str, html: str) -> set[str]:
    soup = BeautifulSoup(html, "lxml")
    base_host = urlparse(base_url).hostname
    links: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if not href:
            continue
        candidate = urljoin(base_url, href)
        parsed = urlparse(candidate)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.hostname != base_host:
            continue
        links.add(candidate)
    return links


def extract_sitemap_links(sitemap_xml: str, host: str) -> set[str]:
    soup = BeautifulSoup(sitemap_xml, "xml")
    urls: set[str] = set()
    for loc in soup.find_all("loc"):
        value = (loc.text or "").strip()
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.hostname == host:
            urls.add(value)
    return urls


def chunk_text(text: str, chunk_size_tokens: int = 800, overlap_tokens: int = 150) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size_tokens - overlap_tokens)
    for start in range(0, len(words), step):
        end = start + chunk_size_tokens
        chunk = words[start:end]
        if not chunk:
            continue
        chunks.append(" ".join(chunk))
        if end >= len(words):
            break
    return chunks

