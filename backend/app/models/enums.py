from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "CITIZEN"
    MODERATOR = "MODERATOR"
    OFFICER = "OFFICER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"


class LocationPrecision(str, Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    USER_ENTERED = "USER_ENTERED"
    UNAVAILABLE = "UNAVAILABLE"


class ReportStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    VERIFIED = "VERIFIED"
    MERGED = "MERGED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class IncidentStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLUTION_UNDER_REVIEW = "RESOLUTION_UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISPUTED = "DISPUTED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class IncidentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ModerationDecisionType(str, Enum):
    VERIFY = "VERIFY"
    MERGE = "MERGE"
    REJECT = "REJECT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    ESCALATE = "ESCALATE"


class AssignmentStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class EvidenceReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DisputeStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
