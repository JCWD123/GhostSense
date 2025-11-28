from fastapi import APIRouter
from app.api.endpoints import tasks, sync, config, logs

router = APIRouter()

router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(sync.router, prefix="/sync", tags=["sync"])
router.include_router(config.router, prefix="/config", tags=["config"])
router.include_router(logs.router, prefix="/logs", tags=["logs"])
