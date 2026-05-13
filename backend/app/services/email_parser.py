"""
Email parsing and analysis service.
Handles RFC 2822 parsing, header extraction, auth result parsing,
link extraction, and threat scoring.
"""
import re
import uuid
import email as email_lib
from email.message import Message
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import dns.resolver
import dns.exception


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_raw_email(raw: str) -> dict:
    """Parse a raw RFC 2822 email into structured fields."""
    msg: Message = email_lib.message_from_string(raw)

    headers = dict(msg.items())
    body = _extract_body(msg)
    relay_path = _parse_received_headers(msg)
    source_ip = _extract_source_ip(relay_path)

    auth = parse_auth_results(headers.get("Authentication-Results", ""))

    return {
        "message_id":  headers.get("Message-ID", "").strip("<>"),
        "sender":      headers.get("From", ""),
        "recipient":   headers.get("To", ""),
        "subject":     headers.get("Subject", ""),
        "raw_headers": headers,
        "raw_body":    body,
        "relay_path":  relay_path,
        "source_ip":   source_ip,
        **auth,
    }


def _extract_body(msg: Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct in ("text/html", "text/plain"):
                try:
                    return part.get_payload(decode=True).decode("utf-8", errors="replace")
                except Exception:
                    pass
        return ""
    try:
        payload = msg.get_payload(decode=True)
        return payload.decode("utf-8", errors="replace") if payload else ""
    except Exception:
        return str(msg.get_payload())


def _parse_received_headers(msg: Message) -> list:
    """Extract relay hops from Received headers."""
    received = msg.get_all("Received") or []
    hops = []
    for r in received:
        hop = {"raw": r.strip()}
        ip_match = re.search(r'\[(\d{1,3}(?:\.\d{1,3}){3})\]', r)
        if ip_match:
            hop["ip"] = ip_match.group(1)
        by_match = re.search(r'by\s+([\w.\-]+)', r)
        if by_match:
            hop["by"] = by_match.group(1)
        hops.append(hop)
    return hops


def _extract_source_ip(relay_path: list) -> Optional[str]:
    if relay_path:
        last = relay_path[-1]
        return last.get("ip")
    return None


# ── Auth result parsing ───────────────────────────────────────────────────────

AUTH_PATTERN = re.compile(
    r'(spf|dkim|dmarc)=(\w+)(?:.*?header\.(?:from|i)=([\w.\-@]+))?',
    re.IGNORECASE,
)


def parse_auth_results(header_value: str) -> dict:
    """Parse Authentication-Results header into SPF/DKIM/DMARC results."""
    result = {
        "spf_result":   None,
        "dkim_result":  None,
        "dmarc_result": None,
        "spf_domain":   None,
        "dkim_domain":  None,
    }
    if not header_value:
        return result

    for match in AUTH_PATTERN.finditer(header_value):
        protocol = match.group(1).lower()
        outcome  = match.group(2).lower()
        domain   = match.group(3)

        if protocol == "spf":
            result["spf_result"] = outcome
            if domain:
                result["spf_domain"] = domain
        elif protocol == "dkim":
            result["dkim_result"] = outcome
            if domain:
                result["dkim_domain"] = domain
        elif protocol == "dmarc":
            result["dmarc_result"] = outcome

    return result


# ── Link extraction ───────────────────────────────────────────────────────────

URL_PATTERN = re.compile(r'https?://[^\s\'"<>]+', re.IGNORECASE)
HREF_PATTERN = re.compile(r'href=["\']?(https?://[^\s\'"<>]+)', re.IGNORECASE)
ANCHOR_PATTERN = re.compile(r'<a[^>]*href=["\']?(https?://[^\s\'"<>]+)["\']?[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)


def extract_links(body: str) -> list[dict]:
    """Extract all URLs from email body with anchor text where available."""
    links = {}

    for match in ANCHOR_PATTERN.finditer(body):
        url = match.group(1)
        anchor = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        parsed = urlparse(url)
        links[url] = {
            "id":          str(uuid.uuid4()),
            "url":         url,
            "domain":      parsed.netloc,
            "is_redirect": _is_redirect_url(url),
            "anchor_text": anchor or None,
        }

    for url in URL_PATTERN.findall(body):
        if url not in links:
            parsed = urlparse(url)
            links[url] = {
                "id":          str(uuid.uuid4()),
                "url":         url,
                "domain":      parsed.netloc,
                "is_redirect": _is_redirect_url(url),
                "anchor_text": None,
            }

    return list(links.values())


REDIRECT_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl",
    "redirect.", "click.", "track.", "link.",
}


def _is_redirect_url(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(r in domain for r in REDIRECT_DOMAINS)


# ── Threat scoring ────────────────────────────────────────────────────────────

def calculate_threat_score(parsed: dict, links: list[dict]) -> tuple[float, list[str]]:
    """
    Calculate a 0-100 threat score and return bypass indicators.
    Higher = more suspicious.
    """
    score = 0.0
    indicators = []

    # Auth failures
    if parsed.get("spf_result") in ("fail", "softfail"):
        score += 20
        indicators.append(f"SPF {parsed['spf_result']}")
    if parsed.get("dkim_result") == "fail":
        score += 20
        indicators.append("DKIM fail")
    if parsed.get("dmarc_result") == "fail":
        score += 25
        indicators.append("DMARC fail")

    # Auth alignment bypass (pass but different domain)
    spf_domain  = parsed.get("spf_domain", "")
    dkim_domain = parsed.get("dkim_domain", "")
    sender      = parsed.get("sender", "")
    if spf_domain and sender and spf_domain.lower() not in sender.lower():
        score += 10
        indicators.append("SPF domain mismatch")
    if dkim_domain and sender and dkim_domain.lower() not in sender.lower():
        score += 10
        indicators.append("DKIM domain mismatch")

    # Suspicious links
    redirect_count = sum(1 for l in links if l["is_redirect"])
    if redirect_count > 0:
        score += min(redirect_count * 5, 15)
        indicators.append(f"{redirect_count} redirect URL(s)")

    if len(links) > 10:
        score += 5
        indicators.append("High link density")

    # No auth results at all
    if not any([parsed.get("spf_result"), parsed.get("dkim_result"), parsed.get("dmarc_result")]):
        score += 10
        indicators.append("No authentication headers")

    return min(round(score, 1), 100.0), indicators
