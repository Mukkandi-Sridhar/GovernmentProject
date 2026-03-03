import pytest

from app.security.ssrf import SSRFViolation, validate_url_against_allowlist


def test_ssrf_blocks_non_allowlisted_host():
    with pytest.raises(SSRFViolation):
        validate_url_against_allowlist(
            "https://example.com/path",
            allowlisted_hosts={"ap.gov.in"},
            allowed_schemes=("https",),
        )

