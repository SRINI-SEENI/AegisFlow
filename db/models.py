import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Any
from sqlalchemy import (
    Column, String, Numeric, DateTime, Date, Enum, Integer, Float, Boolean, 
    ForeignKey, Table, Index, UniqueConstraint, BigInteger, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# --- Enums ---
class KYCStatusEnum(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

class RiskRatingEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AccountTypeEnum(str, enum.Enum):
    CURRENT = "current"
    SAVINGS = "savings"
    CARD = "card"
    WALLET = "wallet"

class AccountStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    DORMANT = "dormant"
    FROZEN = "frozen"
    CLOSED = "closed"

class RuleActionEnum(str, enum.Enum):
    APPROVE = "approve"
    REVIEW = "review"
    DECLINE = "decline"

class RiskBandEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CaseStatusEnum(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_REVIEW = "pending_review"
    CLOSED = "closed"

class DispositionEnum(str, enum.Enum):
    FRAUD = "fraud"
    NOT_FRAUD = "not_fraud"
    SAR_FILED = "sar_filed"


# --- 14 Models matching AegisFlow M1 DDL ---

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_ref: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    kyc_status: Mapped[KYCStatusEnum] = mapped_column(Enum(KYCStatusEnum), default=KYCStatusEnum.PENDING)
    risk_rating: Mapped[RiskRatingEnum] = mapped_column(Enum(RiskRatingEnum), default=RiskRatingEnum.MEDIUM)
    is_pep: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Account(Base):
    __tablename__ = "accounts"
    
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(34), unique=True, nullable=False)
    account_type: Mapped[AccountTypeEnum] = mapped_column(Enum(AccountTypeEnum), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    opened_on: Mapped[date] = mapped_column(Date, nullable=False)
    last_active_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[AccountStatusEnum] = mapped_column(Enum(AccountStatusEnum), default=AccountStatusEnum.ACTIVE)


class Counterparty(Base):
    __tablename__ = "counterparties"
    
    counterparty_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, index=True)
    beneficiary_ref: Mapped[str] = mapped_column(String(64), nullable=False)
    beneficiary_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.account_id"), nullable=False, index=True)
    counterparty_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("counterparties.counterparty_id"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # card, wire, upi
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class VelocitySnapshot(Base):
    __tablename__ = "velocity_snapshots"
    
    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"), unique=True)
    tx_count_1h: Mapped[int] = mapped_column(Integer, default=0)
    tx_count_24h: Mapped[int] = mapped_column(Integer, default=0)
    tx_sum_24h: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
    unique_counterparties_7d: Mapped[int] = mapped_column(Integer, default=0)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RuleDefinition(Base):
    __tablename__ = "rule_definitions"
    
    rule_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action: Mapped[RuleActionEnum] = mapped_column(Enum(RuleActionEnum), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RuleHit(Base):
    __tablename__ = "rule_hits"
    
    hit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"), index=True)
    rule_id: Mapped[str] = mapped_column(String(64), ForeignKey("rule_definitions.rule_id"))
    rule_version: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"), unique=True)
    ml_score: Mapped[float] = mapped_column(Float, nullable=False)
    rules_score: Mapped[float] = mapped_column(Float, nullable=False)
    blended_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_band: Mapped[RiskBandEnum] = mapped_column(Enum(RiskBandEnum), nullable=False)
    decision: Mapped[RuleActionEnum] = mapped_column(Enum(RuleActionEnum), nullable=False)
    reason_codes: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Case(Base):
    __tablename__ = "cases"
    
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[CaseStatusEnum] = mapped_column(Enum(CaseStatusEnum), default=CaseStatusEnum.OPEN)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    disposition: Mapped[Optional[DispositionEnum]] = mapped_column(Enum(DispositionEnum), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CaseAlert(Base):
    __tablename__ = "case_alerts"
    
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), primary_key=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("alerts.alert_id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CaseNote(Base):
    __tablename__ = "case_notes"
    
    note_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"
    
    entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    list_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(200), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
