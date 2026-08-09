from fastapi import APIRouter

from app.api.agent import router as agent_router
from app.api.capabilities import router as capabilities_router
from app.api.health import router as health_router
from app.api.investigations import router as investigations_router
from app.api.tools import router as tools_router

router = APIRouter()
router.include_router(health_router)
router.include_router(agent_router)
router.include_router(investigations_router)
router.include_router(capabilities_router)
router.include_router(tools_router)
