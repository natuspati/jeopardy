"""API routes."""

from fastapi import APIRouter

from api import internal, v1

router = APIRouter(prefix="/api")
router.include_router(v1.router)
router.include_router(internal.router)
