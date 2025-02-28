"""V1 routes."""

from fastapi import APIRouter

from api.v1 import category, user

router = APIRouter(prefix="/v1")
router.include_router(user.router)
router.include_router(category.router)
