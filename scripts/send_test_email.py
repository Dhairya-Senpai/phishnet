#!/usr/bin/env python3
"""
Send a test phishing email to the Phishnet Postfix ingestion service.
Usage: python3 scripts/send_test_email.py
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse

SAMPLE_EMAIL = """\
From: attacker@evil-domain.com
To: victim@phishnet.local
Subject: Urgent: Verify your account immediately
Message-ID: <test-{ts}@evil-domain.com>
Authentication-Results: mx.phishnet.local;
    spf=fail smtp.mailfrom=evil-domain.com;
    dkim=fail header.from=evil-domain.com;
    dmarc=fail header.from=evil-domain.com
Received: from unknown ([192.168.1.100]) by mx.phishnet.local

<html><body>
<p>Your account will be suspended in 24 hours.</p>
<p><a href="https://bit.ly/fake-verify-account">Click here to verify now</a></p>
<p>Or visit: <a href="https://tinyurl.com/reset-credentials">this link</a></p>
</body></html>
"""


def send_test_email(host="localhost", port=2525):
    import time
    raw = SAMPLE_EMAIL.format(ts=int(time.time()))

    msg = MIMEMultipart("alternative")
    msg["From"]    = "attacker@evil-domain.com"
    msg["To"]      = "victim@phishnet.local"
    msg["Subject"] = "Urgent: Verify your account immediately"
    msg.attach(MIMEText(raw, "plain"))

    print(f"Connecting to {host}:{port}...")
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.set_debuglevel(1)
        smtp.sendmail(
            "attacker@evil-domain.com",
            ["victim@phishnet.local"],
            raw,
        )
    print("Email sent successfully. Check the Phishnet dashboard.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send test phishing email to Phishnet")
    parser.add_argument("--host", default="localhost", help="SMTP host (default: localhost)")
    parser.add_argument("--port", type=int, default=2525, help="SMTP port (default: 2525)")
    args = parser.parse_args()
    send_test_email(args.host, args.port)
