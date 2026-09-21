from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.institution import InstitutionOut
from app.models.entities import Institution

router = APIRouter()


@router.get("", response_model=List[InstitutionOut])
def list_institutions(db: Session = Depends(get_db)):
    """List all active institutions."""
    institutions = db.query(Institution).filter(Institution.is_active == True).all()
    return institutions
