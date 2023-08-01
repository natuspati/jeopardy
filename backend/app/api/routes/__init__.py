from fastapi import APIRouter
from app.api.routes.users import router as user_router
from app.api.routes.lobby import router as lobby_router
from app.api.routes.categories import router as category_router
from app.api.routes.questions import router as question_router

router = APIRouter()
# router.include_router(lobby_router, prefix="/lobbies", tags=["lobbies"])
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(category_router, prefix="/categories", tags=["categories"])
router.include_router(question_router, prefix="/categories/{category_id}/questions", tags=["questions"])
