"""Baseline metrics export (docs/specs/09-research/evaluation-protocol.md).

Read-only aggregate reporting for the Phase 2 human-only baseline. Separate from
admin.py, which provisions staff and institutions: auditors need this and must
not have provisioning rights.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.dependencies import rate_limiter, require_roles
from app.core.exceptions import ValidationError
from app.db.session import get_db
from app.models.entities import User
from app.models.enums import UserRole
from app.schemas.metrics import BaselineMetricsOut
from app.services.audit_service import record_audit_event
from app.services.metrics_service import compute_baseline_metrics

router = APIRouter()

# Admins run the programme; auditors inspect it. Nobody else sees cross-case
# aggregates, and moderators in particular must not see their own scorecard
# alongside their colleagues'.
metrics_readers = require_roles([UserRole.ADMIN, UserRole.AUDITOR])


# This endpoint scans whole tables to aggregate. It is role-gated, but a limit
# keeps a stuck dashboard or a retry loop from pinning the database.
@router.get("/baseline", response_model=BaselineMetricsOut, dependencies=[Depends(rate_limiter(30, 60))])
def baseline_metrics(
    request: Request,
    start: Optional[datetime] = Query(
        None, alias="from", description="Inclusive start of the window (ISO 8601). Omit for all history."
    ),
    end: Optional[datetime] = Query(
        None, alias="to", description="Inclusive end of the window (ISO 8601). Omit for up to now."
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(metrics_readers),
):
    """Human-only baseline metrics over an optional date window.

    Metrics the protocol asks for that cannot be derived from system data are
    returned in ``unavailable_metrics`` with collection instructions rather than
    being silently omitted or guessed.
    """
    if start and end and start > end:
        raise ValidationError("The start of the window must not be after its end.")

    result = compute_baseline_metrics(db, start=start, end=end)

    # Reading aggregate programme data is itself a material action.
    record_audit_event(
        db=db,
        entity_type="METRICS",
        entity_id="baseline",
        action="BASELINE_METRICS_EXPORTED",
        actor_id=current_user.id,
        previous_value=None,
        new_value={
            "window_start": start.isoformat() if start else None,
            "window_end": end.isoformat() if end else None,
            "reports_submitted": result.volumes["reports_submitted"],
        },
        reason=f"{current_user.role.value} exported the human-only baseline metrics",
        request_id=request.headers.get("X-Request-ID"),
    )
    db.commit()
    return result
