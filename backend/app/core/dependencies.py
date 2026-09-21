from typing import Optional, List, Callable
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.models.entities import User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Missing authentication token")
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Invalid or expired authentication token")
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise UnauthorizedError("User does not exist or has been deactivated")
    return user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Role {current_user.role.value} is not authorized for this action. Required: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


import time
from collections import defaultdict
from fastapi import Request
from app.core.exceptions import RateLimitedError

_rate_limit_cache = defaultdict(list)


def rate_limiter(max_requests: int = 60, window_seconds: int = 60) -> Callable:
    def limit_checker(request: Request) -> bool:
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{client_ip}:{request.url.path}"
        now = time.time()
        timestamps = [t for t in _rate_limit_cache[key] if now - t < window_seconds]
        if len(timestamps) >= max_requests:
            raise RateLimitedError(retry_after_seconds=window_seconds)
        timestamps.append(now)
        _rate_limit_cache[key] = timestamps
        return True

    return limit_checker

