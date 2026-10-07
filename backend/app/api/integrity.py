from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.integrity import IntegrityOut
from app.services.integrity_service import get_integrity_report

router = APIRouter(prefix="/api/integrity", tags=["integrity"])


@router.get("/{dataset_id}", response_model=IntegrityOut)
def integrity(dataset_id: int, db: Session = Depends(get_db)) -> IntegrityOut:
    return get_integrity_report(db, dataset_id)
