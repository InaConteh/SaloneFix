from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.moderation import ModerationQueueItem, ModerationDecisionCreate
from app.schemas.report import ReportOut
from app.models.entities import User
from app.models.enums import UserRole
from app.core.dependencies import require_roles
from app.core.pagination import PageParams, page_params, paginate
from app.services.moderation_service import get_moderation_queue, moderation_queue_query, process_moderation_decision
from app.services.report_service import get_report_detail

router = APIRouter()


@router.get("/queue", response_model=List[ModerationQueueItem])
def get_queue(
    response: Response,
    category_code: Optional[str] = None,
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    reports = paginate(moderation_queue_query(db, category_code), page, response)
    return get_moderation_queue(db, category_code=category_code, reports=reports)


@router.post("/reports/{report_id}/decision", response_model=ReportOut)
def make_moderation_decision(
    report_id: str,
    decision_in: ModerationDecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    process_moderation_decision(db, report_id, decision_in, current_user, request_id=request_id)
    return get_report_detail(db, report_id, current_user)
