from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum


class DeliveryStatus(str, enum.Enum):
    delivered   = "delivered"
    bounced     = "bounced"
    deferred    = "deferred"
    rejected    = "rejected"
    quarantined = "quarantined"


class AuthResult(str, enum.Enum):
    pass_result = "pass"
    fail        = "fail"
    softfail    = "softfail"
    neutral     = "neutral"
    none        = "none"


class Campaign(Base):
    __tablename__ = "campaigns"

    id:          Mapped[str] = mapped_column(String(36), primary_key=True)
    name:        Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target:      Mapped[str | None] = mapped_column(String(255))  # org/domain being tested
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    emails: Mapped[list["Email"]] = relationship("Email", back_populates="campaign")


class Email(Base):
    __tablename__ = "emails"

    id:              Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id:     Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id"))
    message_id:      Mapped[str | None] = mapped_column(String(512))
    sender:          Mapped[str | None] = mapped_column(String(512))
    recipient:       Mapped[str | None] = mapped_column(String(512))
    subject:         Mapped[str | None] = mapped_column(Text)
    raw_headers:     Mapped[dict | None] = mapped_column(JSON)
    raw_body:        Mapped[str | None] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(
        SAEnum(DeliveryStatus), default=DeliveryStatus.delivered
    )
    received_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source_ip:       Mapped[str | None] = mapped_column(String(64))
    relay_path:      Mapped[list | None] = mapped_column(JSON)   # list of hops

    # Auth results
    spf_result:   Mapped[str | None] = mapped_column(String(32))
    dkim_result:  Mapped[str | None] = mapped_column(String(32))
    dmarc_result: Mapped[str | None] = mapped_column(String(32))
    spf_domain:   Mapped[str | None] = mapped_column(String(255))
    dkim_domain:  Mapped[str | None] = mapped_column(String(255))

    # Analysis
    threat_score:     Mapped[float | None] = mapped_column(Float)
    bypass_indicators: Mapped[list | None] = mapped_column(JSON)
    analysis_notes:   Mapped[str | None] = mapped_column(Text)
    analyzed_at:      Mapped[datetime | None] = mapped_column(DateTime)

    campaign: Mapped["Campaign | None"] = relationship("Campaign", back_populates="emails")
    links:    Mapped[list["ExtractedLink"]] = relationship("ExtractedLink", back_populates="email")


class ExtractedLink(Base):
    __tablename__ = "extracted_links"

    id:          Mapped[str] = mapped_column(String(36), primary_key=True)
    email_id:    Mapped[str] = mapped_column(String(36), ForeignKey("emails.id"))
    url:         Mapped[str] = mapped_column(Text)
    domain:      Mapped[str | None] = mapped_column(String(255))
    is_redirect: Mapped[bool] = mapped_column(default=False)
    anchor_text: Mapped[str | None] = mapped_column(Text)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    email: Mapped["Email"] = relationship("Email", back_populates="links")
