"""V1 routes."""

from fastapi import APIRouter

from api.v1 import category, preset, user

router = APIRouter(prefix="/v1")
router.include_router(user.router)
router.include_router(category.router)
router.include_router(preset.router)
