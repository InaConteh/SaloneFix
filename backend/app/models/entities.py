import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.enums import (
    UserRole,
    LocationPrecision,
    ReportStatus,
    IncidentStatus,
    IncidentPriority,
    ModerationDecisionType,
    AssignmentStatus,
    EvidenceReviewStatus,
    DisputeStatus,
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CITIZEN)
    name_or_alias = Column(String(120), nullable=False)
    contact = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    consent_status = Column(Boolean, default=True, nullable=False)
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="officers")
    reports = relationship("Report", back_populates="reporter")


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    service_area = Column(String(150), nullable=False, default="Freetown")
    contact_channel = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    officers = relationship("User", back_populates="institution")
    assignments = relationship("Assignment", back_populates="institution")


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    requires_resolution_evidence = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    reports = relationship("Report", back_populates="category")
    incidents = relationship("Incident", back_populates="category")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tracking_reference = Column(String(32), unique=True, nullable=False, index=True)
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("service_categories.id"), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_precision = Column(SQLEnum(LocationPrecision), default=LocationPrecision.APPROXIMATE, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_status = Column(SQLEnum(ReportStatus), default=ReportStatus.SUBMITTED, nullable=False, index=True)
    source_channel = Column(String(50), default="WEB", nullable=False)
    idempotency_key = Column(String(128), nullable=True, index=True)
    original_payload_hash = Column(String(64), nullable=False)
    clarification_notes = Column(Text, nullable=True)

    reporter = relationship("User", back_populates="reports")
    category = relationship("ServiceCategory", back_populates="reports")
    media_assets = relationship("MediaAsset", back_populates="report")
    incident_links = relationship("ReportIncidentLink", back_populates="report")
    moderation_decisions = relationship("ModerationDecision", back_populates="report")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("service_categories.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    priority = Column(SQLEnum(IncidentPriority), default=IncidentPriority.MEDIUM, nullable=False)
    lifecycle_status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.VERIFIED, nullable=False, index=True)
    centroid_latitude = Column(Float, nullable=True)
    centroid_longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    category = relationship("ServiceCategory", back_populates="incidents")
    report_links = relationship("ReportIncidentLink", back_populates="incident")
    assignments = relationship("Assignment", back_populates="incident")
    resolution_evidences = relationship("ResolutionEvidence", back_populates="incident")
    disputes = relationship("Dispute", back_populates="incident")


class ReportIncidentLink(Base):
    __tablename__ = "report_incident_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    linked_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    linked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    report = relationship("Report", back_populates="incident_links")
    incident = relationship("Incident", back_populates="report_links")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=True)
    evidence_id = Column(String(36), ForeignKey("resolution_evidence.id"), nullable=True)
    storage_key = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    metadata_status = Column(String(50), default="SANITIZED", nullable=False)
    idempotency_key = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="media_assets")
    evidence = relationship("ResolutionEvidence", back_populates="media_assets", foreign_keys=[evidence_id])


class ModerationDecision(Base):
    __tablename__ = "moderation_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    moderator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(SQLEnum(ModerationDecisionType), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="moderation_decisions")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    assigned_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    declined_at = Column(DateTime, nullable=True)
    decline_reason = Column(Text, nullable=True)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False)

    incident = relationship("Incident", back_populates="assignments")
    institution = relationship("Institution", back_populates="assignments")
    officer = relationship("User", foreign_keys=[officer_id])
    assigner = relationship("User", foreign_keys=[assigned_by])


class ResolutionEvidence(Base):
    __tablename__ = "resolution_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    uploader_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    review_status = Column(SQLEnum(EvidenceReviewStatus), default=EvidenceReviewStatus.PENDING, nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    review_reason = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="resolution_evidences")
    media_assets = relationship("MediaAsset", back_populates="evidence", foreign_keys="MediaAsset.evidence_id")
    uploader = relationship("User", foreign_keys=[uploader_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(DisputeStatus), default=DisputeStatus.SUBMITTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="disputes")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
