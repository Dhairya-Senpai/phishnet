from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.db.session import get_db
from app.core.security import verify_api_key
from app.models.email import Email
from app.schemas.email import OverviewStats
from app.services.ingestion import get_overview_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewStats)
def overview(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Platform-wide analytics overview."""
    return get_overview_stats(db)


@router.get("/threat-distribution")
def threat_distribution(
    campaign_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Threat score distribution bucketed into ranges."""
    q = db.query(Email.threat_score).filter(Email.threat_score.isnot(None))
    if campaign_id:
        q = q.filter(Email.campaign_id == campaign_id)
    scores = [row[0] for row in q.all()]

    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for s in scores:
        if s <= 20:   buckets["0-20"]   += 1
        elif s <= 40: buckets["21-40"]  += 1
        elif s <= 60: buckets["41-60"]  += 1
        elif s <= 80: buckets["61-80"]  += 1
        else:         buckets["81-100"] += 1

    return [{"range": k, "count": v} for k, v in buckets.items()]


@router.get("/auth-timeline")
def auth_timeline(
    days: int = Query(30, le=90),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Daily auth pass/fail counts over the last N days."""
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(Email.received_at).label("date"),
            Email.spf_result,
            func.count(Email.id).label("count"),
        )
        .filter(Email.received_at >= cutoff)
        .group_by(func.date(Email.received_at), Email.spf_result)
        .order_by(func.date(Email.received_at))
        .all()
    )

    by_date = {}
    for row in rows:
        d = str(row.date)
        if d not in by_date:
            by_date[d] = {"date": d, "spf_pass": 0, "spf_fail": 0}
        if row.spf_result == "pass":
            by_date[d]["spf_pass"] += row.count
        elif row.spf_result in ("fail", "softfail"):
            by_date[d]["spf_fail"] += row.count

    return list(by_date.values())


@router.get("/bypass-indicators")
def bypass_indicators(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Most common bypass indicators across all emails."""
    rows = db.query(Email.bypass_indicators).filter(Email.bypass_indicators.isnot(None)).all()
    counts = {}
    for row in rows:
        for indicator in (row[0] or []):
            counts[indicator] = counts.get(indicator, 0) + 1
    return sorted(
        [{"indicator": k, "count": v} for k, v in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
