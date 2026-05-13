"""
Email ingestion service.
Handles storing parsed emails, links, and triggering async analysis.
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.email import Email, ExtractedLink, Campaign
from app.services.email_parser import parse_raw_email, extract_links, calculate_threat_score


def ingest_email(db: Session, raw_email: str, campaign_id: str = None, source_ip: str = None) -> Email:
    """Parse and store a raw email. Returns the stored Email record."""
    parsed = parse_raw_email(raw_email)
    links_data = extract_links(parsed.get("raw_body", ""))
    threat_score, bypass_indicators = calculate_threat_score(parsed, links_data)

    email = Email(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        message_id=parsed.get("message_id"),
        sender=parsed.get("sender"),
        recipient=parsed.get("recipient"),
        subject=parsed.get("subject"),
        raw_headers=parsed.get("raw_headers"),
        raw_body=parsed.get("raw_body"),
        relay_path=parsed.get("relay_path"),
        source_ip=source_ip or parsed.get("source_ip"),
        spf_result=parsed.get("spf_result"),
        dkim_result=parsed.get("dkim_result"),
        dmarc_result=parsed.get("dmarc_result"),
        spf_domain=parsed.get("spf_domain"),
        dkim_domain=parsed.get("dkim_domain"),
        threat_score=threat_score,
        bypass_indicators=bypass_indicators,
        analyzed_at=datetime.utcnow(),
        delivery_status="delivered",
    )

    db.add(email)
    db.flush()

    for link_data in links_data:
        link = ExtractedLink(
            id=link_data["id"],
            email_id=email.id,
            url=link_data["url"],
            domain=link_data["domain"],
            is_redirect=link_data["is_redirect"],
            anchor_text=link_data["anchor_text"],
        )
        db.add(link)

    db.commit()
    db.refresh(email)
    return email


def create_campaign(db: Session, name: str, description: str = None, target: str = None) -> Campaign:
    campaign = Campaign(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        target=target,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def get_overview_stats(db: Session) -> dict:
    from sqlalchemy import func
    from app.models.email import Email, Campaign

    total_emails    = db.query(func.count(Email.id)).scalar() or 0
    total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0

    delivery_counts = (
        db.query(Email.delivery_status, func.count(Email.id))
        .group_by(Email.delivery_status)
        .all()
    )
    delivery = {s: c for s, c in delivery_counts}

    def auth_counts(field, value):
        return db.query(func.count(Email.id)).filter(field == value).scalar() or 0

    avg_score = db.query(func.avg(Email.threat_score)).scalar()

    return {
        "total_emails":    total_emails,
        "total_campaigns": total_campaigns,
        "delivery": {
            "total":       total_emails,
            "delivered":   delivery.get("delivered", 0),
            "bounced":     delivery.get("bounced", 0),
            "rejected":    delivery.get("rejected", 0),
            "quarantined": delivery.get("quarantined", 0),
        },
        "auth": {
            "spf_pass":   auth_counts(Email.spf_result,   "pass"),
            "spf_fail":   auth_counts(Email.spf_result,   "fail"),
            "dkim_pass":  auth_counts(Email.dkim_result,  "pass"),
            "dkim_fail":  auth_counts(Email.dkim_result,  "fail"),
            "dmarc_pass": auth_counts(Email.dmarc_result, "pass"),
            "dmarc_fail": auth_counts(Email.dmarc_result, "fail"),
        },
        "avg_threat_score":    round(float(avg_score), 1) if avg_score else None,
        "recent_bypass_count": db.query(func.count(Email.id)).filter(Email.threat_score >= 60).scalar() or 0,
    }
