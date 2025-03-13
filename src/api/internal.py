from fastapi import APIRouter

router = APIRouter(prefix="/internal")


@router.get("/health")
async def health():
    """Health check."""
    return "healthy"
