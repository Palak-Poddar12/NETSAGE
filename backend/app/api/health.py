from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(tags=["Health"])


@router.get("/health")
def api_health_check():
    """
    Lightweight health probe used by the NetSage frontend for live
    connection status (Sidebar/Topbar indicator).
    Returns {"status": "healthy"} when the service and database are reachable.
    """
    db_status = "connected"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "NetSage AI Backend",
        "database": db_status,
    }