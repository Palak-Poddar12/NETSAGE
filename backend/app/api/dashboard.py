from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics", response_model=DashboardMetricsResponse, status_code=status.HTTP_200_OK)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns live dynamic dashboard metrics calculated directly from database records.
    """
    return dashboard_service.get_metrics(db=db)
