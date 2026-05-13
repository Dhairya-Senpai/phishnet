from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "phishnet",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.worker"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def analyze_email_task(self, email_id: str):
    """Async task for deep email analysis (DNS lookups, link checks, etc.)"""
    from app.db.session import SessionLocal
    from app.models.email import Email
    from app.services.email_parser import parse_auth_results, calculate_threat_score

    db = SessionLocal()
    try:
        email_record = db.query(Email).filter(Email.id == email_id).first()
        if not email_record:
            return {"status": "not_found", "email_id": email_id}

        # Re-score with full analysis
        parsed = {
            "spf_result":   email_record.spf_result,
            "dkim_result":  email_record.dkim_result,
            "dmarc_result": email_record.dmarc_result,
            "spf_domain":   email_record.spf_domain,
            "dkim_domain":  email_record.dkim_domain,
            "sender":       email_record.sender,
        }
        links = [{"is_redirect": l.is_redirect} for l in email_record.links]
        score, indicators = calculate_threat_score(parsed, links)

        email_record.threat_score = score
        email_record.bypass_indicators = indicators
        db.commit()

        return {"status": "complete", "email_id": email_id, "threat_score": score}

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
