import logging
from typing import Iterable, Optional
from sqlalchemy.orm import Session
from app.models.entities import Incident, Notification, Report, ReportIncidentLink, User
from app.models.enums import UserRole

logger = logging.getLogger("salonefix.notifications")

# Delivery channels. IN_APP is the only channel in the Human-First phase; any
# future email/SMS/WhatsApp adapter registers here behind a feature flag and
# must be a no-op when its configuration is absent.
CHANNEL_IN_APP = "IN_APP"


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Optional[Notification]:
    """Create a persistent in-app notification.

    Delivery problems are logged (structured) and never raised: a failed
    notification must not roll back the material action that triggered it.
    """
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        db.add(notif)
        logger.debug(
            "notification_queued",
            extra={"data": {"channel": CHANNEL_IN_APP, "user_id": user_id, "entity_type": entity_type, "entity_id": entity_id}},
        )
        return notif
    except Exception:  # pragma: no cover - defensive; SQLAlchemy add() rarely fails
        logger.exception(
            "notification_delivery_failed",
            extra={"data": {"channel": CHANNEL_IN_APP, "user_id": user_id, "entity_type": entity_type, "entity_id": entity_id, "title": title}},
        )
        return None


def notify_users(
    db: Session,
    user_ids: Iterable[str],
    title: str,
    message: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> list[Notification]:
    notifications: list[Notification] = []
    for user_id in dict.fromkeys(uid for uid in user_ids if uid):
        notif = create_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        if notif is not None:
            notifications.append(notif)
    return notifications


def notify_reporter(
    db: Session,
    report: Report,
    title: str,
    message: str,
    entity_type: str = "REPORT",
) -> list[Notification]:
    return notify_users(db, [report.reporter_id], title, message, entity_type, report.id)


def notify_incident_reporters(
    db: Session,
    incident: Incident,
    title: str,
    message: str,
) -> list[Notification]:
    reporter_ids = [
        link.report.reporter_id
        for link in db.query(ReportIncidentLink).filter(ReportIncidentLink.incident_id == incident.id).all()
        if link.report
    ]
    return notify_users(db, reporter_ids, title, message, "INCIDENT", incident.id)


def notify_institution_officers(
    db: Session,
    institution_id: str,
    title: str,
    message: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    officer_id: Optional[str] = None,
) -> list[Notification]:
    query = db.query(User).filter(
        User.role == UserRole.OFFICER,
        User.institution_id == institution_id,
        User.is_active == True,
    )
    if officer_id:
        query = query.filter(User.id == officer_id)
    return notify_users(db, [user.id for user in query.all()], title, message, entity_type, entity_id)


def notify_roles(
    db: Session,
    roles: Iterable[UserRole],
    title: str,
    message: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> list[Notification]:
    users = db.query(User).filter(User.role.in_(list(roles)), User.is_active == True).all()
    return notify_users(db, [user.id for user in users], title, message, entity_type, entity_id)
