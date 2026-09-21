"""Administrator endpoints: staff provisioning and institution management.

Every mutation records an audit event with the administrator's reason.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserOut
from app.schemas.institution import InstitutionOut
from app.schemas.admin import StaffUserCreate, UserAdminUpdate, InstitutionCreate, InstitutionUpdate
from app.models.entities import User, Institution
from app.models.enums import UserRole
from app.core.dependencies import require_roles
from app.core.exceptions import NotFoundError, ValidationError, StateConflictError
from app.core.pagination import PageParams, page_params, paginate
from app.core.security import hash_password
from app.services.audit_service import record_audit_event

router = APIRouter()

admin_only = require_roles([UserRole.ADMIN])


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        role=user.role,
        name_or_alias=user.name_or_alias,
        contact=user.contact,
        institution_id=user.institution_id,
        institution_name=user.institution.name if user.institution else None,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _require_institution(db: Session, institution_id: Optional[str], role: UserRole) -> None:
    if role == UserRole.OFFICER:
        if not institution_id:
            raise ValidationError("An officer account must belong to an institution.")
        if not db.query(Institution).filter(Institution.id == institution_id, Institution.is_active == True).first():
            raise NotFoundError("Institution")
    elif institution_id and not db.query(Institution).filter(Institution.id == institution_id).first():
        raise NotFoundError("Institution")


# --------------------------------------------------------------------------- users
@router.get("/users", response_model=List[UserOut])
def list_users(
    response: Response,
    role: Optional[UserRole] = None,
    include_inactive: bool = True,
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if not include_inactive:
        query = query.filter(User.is_active == True)
    users = paginate(query.order_by(User.created_at.desc()), page, response)
    return [user_out(u) for u in users]


@router.post("/users", response_model=UserOut, status_code=201)
def create_staff_user(
    user_in: StaffUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    contact = user_in.contact.strip().lower()
    if db.query(User).filter(User.contact == contact).first():
        raise ValidationError("An account with this contact already exists.")
    _require_institution(db, user_in.institution_id, user_in.role)

    user = User(
        name_or_alias=user_in.name_or_alias.strip(),
        contact=contact,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        institution_id=user_in.institution_id if user_in.role == UserRole.OFFICER else None,
        consent_status=True,
        is_active=True,
    )
    db.add(user)
    db.flush()
    record_audit_event(
        db=db,
        entity_type="USER",
        entity_id=user.id,
        action="USER_PROVISIONED",
        actor_id=current_user.id,
        previous_value=None,
        new_value={"role": user.role.value, "institution_id": user.institution_id, "contact": user.contact},
        reason="Administrator provisioned a staff account",
        request_id=request.headers.get("X-Request-ID"),
    )
    db.commit()
    db.refresh(user)
    return user_out(user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    update_in: UserAdminUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")
    if user.id == current_user.id and update_in.is_active is False:
        raise StateConflictError("You cannot deactivate your own administrator account.")
    if user.id == current_user.id and update_in.role and update_in.role != UserRole.ADMIN:
        raise StateConflictError("You cannot remove your own administrator role.")

    previous = {"role": user.role.value, "is_active": user.is_active, "institution_id": user.institution_id}
    new_role = update_in.role or user.role
    new_institution = update_in.institution_id if update_in.institution_id is not None else user.institution_id
    _require_institution(db, new_institution, new_role)

    user.role = new_role
    user.institution_id = new_institution if new_role == UserRole.OFFICER else None
    if update_in.is_active is not None:
        user.is_active = update_in.is_active

    record_audit_event(
        db=db,
        entity_type="USER",
        entity_id=user.id,
        action="USER_UPDATED",
        actor_id=current_user.id,
        previous_value=previous,
        new_value={"role": user.role.value, "is_active": user.is_active, "institution_id": user.institution_id},
        reason=update_in.reason,
        request_id=request.headers.get("X-Request-ID"),
    )
    db.commit()
    db.refresh(user)
    return user_out(user)


# --------------------------------------------------------------------- institutions
@router.post("/institutions", response_model=InstitutionOut, status_code=201)
def create_institution(
    inst_in: InstitutionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    name = inst_in.name.strip()
    if db.query(Institution).filter(Institution.name == name).first():
        raise ValidationError("An institution with this name already exists.")
    inst = Institution(
        name=name,
        description=inst_in.description,
        service_area=inst_in.service_area.strip(),
        contact_channel=inst_in.contact_channel,
        is_active=True,
    )
    db.add(inst)
    db.flush()
    record_audit_event(
        db=db,
        entity_type="INSTITUTION",
        entity_id=inst.id,
        action="INSTITUTION_CREATED",
        actor_id=current_user.id,
        previous_value=None,
        new_value={"name": inst.name, "service_area": inst.service_area},
        reason="Administrator registered a responding institution",
        request_id=request.headers.get("X-Request-ID"),
    )
    db.commit()
    db.refresh(inst)
    return inst


@router.patch("/institutions/{institution_id}", response_model=InstitutionOut)
def update_institution(
    institution_id: str,
    update_in: InstitutionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise NotFoundError("Institution")
    changes = update_in.model_dump(exclude_unset=True)
    previous = {field: getattr(inst, field) for field in changes}
    for field, value in changes.items():
        setattr(inst, field, value)
    record_audit_event(
        db=db,
        entity_type="INSTITUTION",
        entity_id=inst.id,
        action="INSTITUTION_UPDATED",
        actor_id=current_user.id,
        previous_value=previous,
        new_value=changes,
        reason="Administrator updated institution details",
        request_id=request.headers.get("X-Request-ID"),
    )
    db.commit()
    db.refresh(inst)
    return inst
