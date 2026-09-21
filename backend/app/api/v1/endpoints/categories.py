from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.institution import ServiceCategoryOut
from app.models.entities import ServiceCategory

router = APIRouter()


@router.get("", response_model=List[ServiceCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all active service categories."""
    categories = db.query(ServiceCategory).filter(ServiceCategory.is_active == True).all()
    return categories
