from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.investigations import router as investigations_router

router = APIRouter()
router.include_router(health_router)
router.include_router(investigations_router)
