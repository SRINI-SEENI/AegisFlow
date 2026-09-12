import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import (
    Column, String, Numeric, DateTime, Enum, Integer, Float, Boolean, 
    ForeignKey, Table, Index, UniqueConstraint, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# --- Enums ---
class RiskTierEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ChannelEnum(str, enum.Enum):
    CARD = "card"
    TRANSFER = "transfer"
    WALLET = "wallet"

class DecisionEnum(str, enum.Enum):
    APPROVE = "approve"
    REVIEW = "review"
    DECLINE = "decline"

class CaseStatusEnum(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_REVIEW = "pending_review"
    CLOSED = "closed"

class DispositionEnum(str, enum.Enum):
    FRAUD = "fraud"
    NOT_FRAUD = "not_fraud"
    SAR_FILED = "sar_filed"

class EvidenceKindEnum(str, enum.Enum):
    GRAPH = "graph"
    TIMELINE = "timeline"
    TYPOLOGY = "typology"
    MEDIA = "media"
    NOTE = "note"

class AuthorKindEnum(str, enum.Enum):
    AGENT = "agent"
    HUMAN = "human"
    ANALYST = "analyst"

class SARStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    EDITED = "edited"
    APPROVED = "approved"
    REJECTED = "rejected"

# --- Models ---

class Account(Base):
    __tablename__ = "accounts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    risk_tier: Mapped[RiskTierEnum] = mapped_column(Enum(RiskTierEnum), default=RiskTierEnum.LOW, index=True)
    kyc_level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="active")

class Device(Base):
    __tablename__ = "devices"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fingerprint: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reputation: Mapped[float] = mapped_column(Float, default=1.0)

class IPAddress(Base):
    __tablename__ = "ips"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip: Mapped[str] = mapped_column(INET, unique=True, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reputation: Mapped[float] = mapped_column(Float, default=1.0)

class Merchant(Base):
    __tablename__ = "merchants"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mcc: Mapped[str] = mapped_column(String(10), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reputation: Mapped[float] = mapped_column(Float, default=1.0)

class EntityEdge(Base):
    __tablename__ = "entity_edges"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    src_type: Mapped[str] = mapped_column(String(32), nullable=False)
    src_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dst_type: Mapped[str] = mapped_column(String(32), nullable=False)
    dst_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    edge_type: Mapped[str] = mapped_column(String(32), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    __table_args__ = (
        Index("idx_entity_edge_src", "src_type", "src_id"),
        Index("idx_entity_edge_dst", "dst_type", "dst_id"),
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), index=True)
    counterparty_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    merchant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=True)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    ip_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("ips.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    channel: Mapped[ChannelEnum] = mapped_column(Enum(ChannelEnum), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="processed")

class Decision(Base):
    __tablename__ = "decisions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), unique=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    calibrated_prob: Mapped[float] = mapped_column(Float, nullable=False)
    decision: Mapped[DecisionEnum] = mapped_column(Enum(DecisionEnum), nullable=False, index=True)
    reason_codes: Mapped[dict] = mapped_column(JSONB, default=list)
    rule_hits: Mapped[dict] = mapped_column(JSONB, default=list)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    degraded: Mapped[bool] = mapped_column(Boolean, default=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Case(Base):
    __tablename__ = "cases"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[CaseStatusEnum] = mapped_column(Enum(CaseStatusEnum), default=CaseStatusEnum.OPEN)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sla_due: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    disposition: Mapped[Optional[DispositionEnum]] = mapped_column(Enum(DispositionEnum), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"))
    kind: Mapped[EvidenceKindEnum] = mapped_column(Enum(EvidenceKindEnum), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_ref: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_by: Mapped[AuthorKindEnum] = mapped_column(Enum(AuthorKindEnum), default=AuthorKindEnum.AGENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class SARDraft(Base):
    __tablename__ = "sar_drafts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    narrative_md: Mapped[str] = mapped_column(String, nullable=False)
    citations: Mapped[dict] = mapped_column(JSONB, default=list)
    status: Mapped[SARStatusEnum] = mapped_column(Enum(SARStatusEnum), default=SARStatusEnum.DRAFT)
    author: Mapped[AuthorKindEnum] = mapped_column(Enum(AuthorKindEnum), default=AuthorKindEnum.AGENT)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("case_id", "version", name="uq_case_sar_version"),
    )
