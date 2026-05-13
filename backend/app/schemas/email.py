from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ── Campaign ──────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target: Optional[str] = None


class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    target: Optional[str]
    created_at: datetime
    email_count: int = 0

    model_config = {"from_attributes": True}


# ── Email ─────────────────────────────────────────────────────────────────────

class EmailIngest(BaseModel):
    """Payload for manual email ingestion via API."""
    raw_email: str          # full RFC 2822 email as string
    campaign_id: Optional[str] = None
    source_ip: Optional[str] = None


class AuthResults(BaseModel):
    spf: Optional[str] = None
    dkim: Optional[str] = None
    dmarc: Optional[str] = None
    spf_domain: Optional[str] = None
    dkim_domain: Optional[str] = None


class LinkResponse(BaseModel):
    id: str
    url: str
    domain: Optional[str]
    is_redirect: bool
    anchor_text: Optional[str]

    model_config = {"from_attributes": True}


class EmailResponse(BaseModel):
    id: str
    campaign_id: Optional[str]
    message_id: Optional[str]
    sender: Optional[str]
    recipient: Optional[str]
    subject: Optional[str]
    delivery_status: str
    received_at: datetime
    source_ip: Optional[str]
    relay_path: Optional[list]
    spf_result: Optional[str]
    dkim_result: Optional[str]
    dmarc_result: Optional[str]
    threat_score: Optional[float]
    bypass_indicators: Optional[list]
    analysis_notes: Optional[str]
    analyzed_at: Optional[datetime]
    links: List[LinkResponse] = []

    model_config = {"from_attributes": True}


class EmailSummary(BaseModel):
    id: str
    sender: Optional[str]
    recipient: Optional[str]
    subject: Optional[str]
    delivery_status: str
    received_at: datetime
    threat_score: Optional[float]
    spf_result: Optional[str]
    dkim_result: Optional[str]
    dmarc_result: Optional[str]

    model_config = {"from_attributes": True}


# ── Analytics ─────────────────────────────────────────────────────────────────

class DeliveryStats(BaseModel):
    total: int
    delivered: int
    bounced: int
    rejected: int
    quarantined: int


class AuthStats(BaseModel):
    spf_pass: int
    spf_fail: int
    dkim_pass: int
    dkim_fail: int
    dmarc_pass: int
    dmarc_fail: int


class OverviewStats(BaseModel):
    total_emails: int
    total_campaigns: int
    delivery: DeliveryStats
    auth: AuthStats
    avg_threat_score: Optional[float]
    recent_bypass_count: int
