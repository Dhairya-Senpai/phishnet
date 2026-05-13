"""
Tests for Phishnet backend services.
Run: pytest tests/ -v
"""
import pytest
from app.services.email_parser import (
    parse_raw_email,
    parse_auth_results,
    extract_links,
    calculate_threat_score,
)

# ── Sample emails ─────────────────────────────────────────────────────────────

SAMPLE_EMAIL_PASS = """\
From: legitimate@example.com
To: victim@target.com
Subject: Invoice Q3
Message-ID: <abc123@example.com>
Authentication-Results: mx.target.com;
    spf=pass smtp.mailfrom=example.com;
    dkim=pass header.i=@example.com;
    dmarc=pass header.from=example.com
Received: from mail.example.com ([1.2.3.4]) by mx.target.com

Click here: <a href="https://example.com/invoice">View Invoice</a>
"""

SAMPLE_EMAIL_FAIL = """\
From: phisher@evil.com
To: victim@target.com
Subject: Urgent: Reset your password
Message-ID: <xyz789@evil.com>
Authentication-Results: mx.target.com;
    spf=fail smtp.mailfrom=evil.com;
    dkim=fail header.i=@evil.com;
    dmarc=fail header.from=evil.com
Received: from unknown ([9.9.9.9]) by mx.target.com

Click: <a href="https://bit.ly/abc123">Reset Now</a>
Also: <a href="https://tinyurl.com/xyz">Click here</a>
"""

SAMPLE_EMAIL_NO_AUTH = """\
From: noauth@suspicious.com
To: victim@target.com
Subject: You won!

Visit https://malicious.example.com/win?ref=abc for your prize
"""


# ── Parser tests ──────────────────────────────────────────────────────────────

def test_parse_raw_email_extracts_fields():
    parsed = parse_raw_email(SAMPLE_EMAIL_PASS)
    assert parsed["sender"] == "legitimate@example.com"
    assert parsed["recipient"] == "victim@target.com"
    assert parsed["subject"] == "Invoice Q3"
    assert parsed["message_id"] == "abc123@example.com"


def test_parse_auth_results_pass():
    header = "mx.target.com; spf=pass smtp.mailfrom=example.com; dkim=pass header.i=@example.com; dmarc=pass"
    result = parse_auth_results(header)
    assert result["spf_result"] == "pass"
    assert result["dkim_result"] == "pass"
    assert result["dmarc_result"] == "pass"


def test_parse_auth_results_fail():
    header = "mx.target.com; spf=fail smtp.mailfrom=evil.com; dkim=fail; dmarc=fail"
    result = parse_auth_results(header)
    assert result["spf_result"] == "fail"
    assert result["dkim_result"] == "fail"
    assert result["dmarc_result"] == "fail"


def test_parse_auth_results_empty():
    result = parse_auth_results("")
    assert result["spf_result"] is None
    assert result["dkim_result"] is None
    assert result["dmarc_result"] is None


# ── Link extraction tests ─────────────────────────────────────────────────────

def test_extract_links_finds_anchor_hrefs():
    body = '<a href="https://example.com/page">Click here</a>'
    links = extract_links(body)
    assert len(links) == 1
    assert links[0]["url"] == "https://example.com/page"
    assert links[0]["anchor_text"] == "Click here"
    assert links[0]["domain"] == "example.com"


def test_extract_links_detects_redirects():
    body = '<a href="https://bit.ly/abc">Short link</a>'
    links = extract_links(body)
    assert links[0]["is_redirect"] is True


def test_extract_links_plain_url():
    body = "Visit https://example.com/win for your prize"
    links = extract_links(body)
    assert any(l["url"] == "https://example.com/win" for l in links)


def test_extract_links_deduplicates():
    body = '<a href="https://example.com">One</a> <a href="https://example.com">Two</a>'
    links = extract_links(body)
    urls = [l["url"] for l in links]
    assert len(urls) == len(set(urls))


# ── Threat scoring tests ──────────────────────────────────────────────────────

def test_threat_score_low_for_passing_auth():
    parsed = parse_raw_email(SAMPLE_EMAIL_PASS)
    links = extract_links(parsed["raw_body"])
    score, indicators = calculate_threat_score(parsed, links)
    assert score < 30
    assert len(indicators) == 0 or "redirect" not in str(indicators).lower()


def test_threat_score_high_for_failing_auth():
    parsed = parse_raw_email(SAMPLE_EMAIL_FAIL)
    links = extract_links(parsed["raw_body"])
    score, indicators = calculate_threat_score(parsed, links)
    assert score >= 60
    assert any("SPF" in i or "DKIM" in i or "DMARC" in i for i in indicators)


def test_threat_score_flags_no_auth():
    parsed = parse_raw_email(SAMPLE_EMAIL_NO_AUTH)
    links = extract_links(parsed["raw_body"])
    score, indicators = calculate_threat_score(parsed, links)
    assert "No authentication headers" in indicators


def test_threat_score_flags_redirect_urls():
    parsed = parse_raw_email(SAMPLE_EMAIL_FAIL)
    links = extract_links(parsed["raw_body"])
    score, indicators = calculate_threat_score(parsed, links)
    assert any("redirect" in i.lower() for i in indicators)


def test_threat_score_capped_at_100():
    parsed = {
        "spf_result": "fail", "dkim_result": "fail", "dmarc_result": "fail",
        "spf_domain": "evil.com", "dkim_domain": "evil.com", "sender": "x@other.com"
    }
    links = [{"is_redirect": True}] * 20
    score, _ = calculate_threat_score(parsed, links)
    assert score <= 100
