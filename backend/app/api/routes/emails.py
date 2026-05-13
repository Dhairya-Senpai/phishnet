from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.core.security import verify_api_key
from app.models.email import Email
from app.schemas.email import EmailIngest, EmailResponse, EmailSummary
from app.services.ingestion import ingest_email

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/ingest", response_model=EmailResponse)
def ingest(
    payload: EmailIngest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Ingest a raw email for analysis."""
    try:
        record = ingest_email(
            db,
            raw_email=payload.raw_email,
            campaign_id=payload.campaign_id,
            source_ip=payload.source_ip,
        )
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/", response_model=List[EmailSummary])
def list_emails(
    campaign_id: Optional[str] = Query(None),
    delivery_status: Optional[str] = Query(None),
    min_threat_score: Optional[float] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """List ingested emails with optional filters."""
    q = db.query(Email)
    if campaign_id:
        q = q.filter(Email.campaign_id == campaign_id)
    if delivery_status:
        q = q.filter(Email.delivery_status == delivery_status)
    if min_threat_score is not None:
        q = q.filter(Email.threat_score >= min_threat_score)
    return q.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Get full email details including links and analysis."""
    record = db.query(Email).filter(Email.id == email_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Email not found")
    return record


@router.delete("/{email_id}", status_code=204)
def delete_email(
    email_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    record = db.query(Email).filter(Email.id == email_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Email not found")
    db.delete(record)
    db.commit()
