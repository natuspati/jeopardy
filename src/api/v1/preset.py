from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from auth import get_current_user
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.preset import PaginatedBasicPresetSchema
from jlib.schemas.user import UserSchema
from jlib.services import BasePresetService
from jlib.utils.response import generate_responses
from services import PresetService

router = APIRouter(prefix="/preset", tags=["preset"])


@router.get(
    "/",
    response_model=PaginatedBasicPresetSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
    ),
)
async def get_presets(
    pagination: Annotated[PaginationSchema, Query()],
    user: Annotated[UserSchema, Depends(get_current_user)],
    preset_service: Annotated[BasePresetService, Depends(PresetService)],
):
    return await preset_service.get_presets(
        user_id=user.id,
        pagination=pagination,
    )
