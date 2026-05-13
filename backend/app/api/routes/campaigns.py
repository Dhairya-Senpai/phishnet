from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.session import get_db
from app.core.security import verify_api_key
from app.models.email import Campaign, Email
from app.schemas.email import CampaignCreate, CampaignResponse
from app.services.ingestion import create_campaign

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse)
def create(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return create_campaign(db, payload.name, payload.description, payload.target)


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    result = []
    for c in campaigns:
        count = db.query(func.count(Email.id)).filter(Email.campaign_id == c.id).scalar() or 0
        d = CampaignResponse.model_validate(c)
        d.email_count = count
        result.append(d)
    return result


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    count = db.query(func.count(Email.id)).filter(Email.campaign_id == campaign_id).scalar() or 0
    d = CampaignResponse.model_validate(c)
    d.email_count = count
    return d


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(c)
    db.commit()
