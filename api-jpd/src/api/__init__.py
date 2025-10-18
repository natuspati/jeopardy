from fastapi import APIRouter

from api import internal, v1

router = APIRouter(prefix="/api")

router.include_router(internal.router)
router.include_router(v1.router)
