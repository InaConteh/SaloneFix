from typing import List
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.notification import NotificationOut
from app.models.entities import Notification, User
from app.core.dependencies import get_current_user
from app.core.pagination import PageParams, page_params, paginate
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.get("", response_model=List[NotificationOut])
def list_my_notifications(
    response: Response,
    unread_only: bool = False,
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return paginate(query.order_by(Notification.created_at.desc()), page, response)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise NotFoundError("Notification")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
