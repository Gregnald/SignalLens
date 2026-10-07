from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import DashboardOut
from app.services.dashboard_service import get_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{dataset_id}", response_model=DashboardOut)
def dashboard(dataset_id: int, db: Session = Depends(get_db)) -> DashboardOut:
    return get_dashboard(db, dataset_id)
