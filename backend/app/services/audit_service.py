import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.entities import AuditEvent


def record_audit_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: Optional[str] = None,
    previous_value: Any = None,
    new_value: Any = None,
    reason: Optional[str] = None,
    request_id: Optional[str] = None,
) -> AuditEvent:
    """Record an immutable, append-only audit event in the database."""
    prev_str = json.dumps(previous_value) if isinstance(previous_value, (dict, list)) else (str(previous_value) if previous_value is not None else None)
    new_str = json.dumps(new_value) if isinstance(new_value, (dict, list)) else (str(new_value) if new_value is not None else None)

    event = AuditEvent(
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        previous_value=prev_str,
        new_value=new_str,
        reason=reason,
        request_id=request_id,
    )
    db.add(event)
    return event
