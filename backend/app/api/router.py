from fastapi import APIRouter

from app.api.cases import router as cases_router
from app.api.diagnoses import router as diagnoses_router
from app.api.health import router as health_router
from app.api.reviews import router as reviews_router
from app.api.dashboard import router as dashboard_router
from app.api.packet_tracer import router as packet_tracer_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(cases_router)
api_router.include_router(diagnoses_router)
api_router.include_router(reviews_router)
api_router.include_router(dashboard_router)
api_router.include_router(packet_tracer_router)
