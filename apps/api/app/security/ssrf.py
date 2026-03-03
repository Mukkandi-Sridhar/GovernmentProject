from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFViolation(Exception):
    pass


def _is_blocked_ip(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_link_local
    )


def validate_url_against_allowlist(url: str, allowlisted_hosts: set[str], allowed_schemes: tuple[str, ...]) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in allowed_schemes:
        raise SSRFViolation(f"Unsupported scheme: {parsed.scheme}")

    host = (parsed.hostname or "").lower().strip()
    if not host:
        raise SSRFViolation("Missing host")

    if host not in allowlisted_hosts:
        raise SSRFViolation("Host not allowlisted")

    try:
        addresses = socket.getaddrinfo(host, parsed.port or 443)
    except socket.gaierror as exc:
        raise SSRFViolation("Unable to resolve host") from exc

    for _, _, _, _, sockaddr in addresses:
        ip_text = sockaddr[0]
        if _is_blocked_ip(ip_text):
            raise SSRFViolation(f"Blocked destination IP: {ip_text}")

