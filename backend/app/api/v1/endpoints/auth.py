from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.models.entities import User
from app.models.enums import UserRole
from app.core.security import verify_password, hash_password, create_access_token
from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.dependencies import get_current_user, rate_limiter

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(rate_limiter(max_requests=20, window_seconds=60)),
):
    user = db.query(User).filter(User.contact == login_in.contact.strip().lower()).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise UnauthorizedError("Invalid contact or password.")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive.")

    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse)
def register(
    reg_in: RegisterRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(rate_limiter(max_requests=10, window_seconds=60)),
):
    existing = db.query(User).filter(User.contact == reg_in.contact.strip().lower()).first()
    if existing:
        raise ValidationError("An account with this contact already exists.")

    # Public self-registration only ever creates citizens. Staff roles
    # (moderator/officer/admin/auditor) are provisioned by an administrator
    # via /admin/users so nobody can escalate their own privileges.
    user = User(
        name_or_alias=reg_in.name_or_alias.strip(),
        contact=reg_in.contact.strip().lower(),
        password_hash=hash_password(reg_in.password),
        role=UserRole.CITIZEN,
        institution_id=None,
        consent_status=reg_in.consent_status,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
