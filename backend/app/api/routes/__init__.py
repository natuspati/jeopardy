from fastapi import APIRouter
from app.api.routes.lobby import router as lobby_router
from app.api.routes.categories import router as category_router

router = APIRouter()
# router.include_router(lobby_router, prefix="/lobbies", tags=["lobbies"])
router.include_router(category_router, prefix="/categories", tags=["categories"])
