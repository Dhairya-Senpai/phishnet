#!/usr/bin/env python3
"""
Postfix pipe script.
Reads a raw email from stdin and POSTs it to the Phishnet API for analysis.
Called by Postfix with: argv=/usr/local/bin/pipe_to_api.py ${sender} ${recipient}
"""
import sys
import os
import json
import urllib.request
import urllib.error
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [pipe_to_api] %(levelname)s: %(message)s",
    stream=sys.stderr,
)

# Load env from file if it exists (Postfix strips environment)
_env_file = "/etc/postfix/pipe_env"
if os.path.exists(_env_file):
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

API_URL = os.environ.get("PHISHNET_API_URL", "http://backend:8000")
API_KEY = os.environ.get("PHISHNET_API_KEY", "change-me-in-production")


def main():
    sender    = sys.argv[1] if len(sys.argv) > 1 else ""
    recipient = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        raw_email = sys.stdin.read()
    except Exception as e:
        logging.error(f"Failed to read email from stdin: {e}")
        sys.exit(75)

    if not raw_email.strip():
        logging.warning("Empty email received, skipping")
        sys.exit(0)

    logging.info(f"Received email from={sender} to={recipient} size={len(raw_email)}")

    payload = json.dumps({
        "raw_email":   raw_email,
        "source_ip":   None,
        "campaign_id": None,
    }).encode("utf-8")

    req = urllib.request.Request(
        url=f"{API_URL}/api/v1/emails/ingest",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key":    API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body   = resp.read().decode("utf-8")
            result = json.loads(body)
            logging.info(f"Ingested id={result.get('id')} threat_score={result.get('threat_score')}")
            sys.exit(0)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logging.error(f"API returned HTTP {e.code}: {body}")
        sys.exit(69 if e.code < 500 else 75)

    except urllib.error.URLError as e:
        logging.error(f"Could not reach API: {e.reason}")
        sys.exit(75)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(75)


if __name__ == "__main__":
    main()
