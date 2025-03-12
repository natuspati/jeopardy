from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from auth import get_current_user
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
    PresetCreateShowSchema,
)
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


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BasicPresetSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "Wrong data provided"),
    ),
)
async def create_preset(
    user: Annotated[UserSchema, Depends(get_current_user)],
    preset_service: Annotated[BasePresetService, Depends(PresetService)],
    preset_create: Annotated[PresetCreateShowSchema | None, Body()] = None,
):
    preset_data = {"owner_id": user.id} | (
        preset_create.model_dump() if preset_create else {}
    )
    return await preset_service.create_preset(
        preset=PresetCreateSchema.model_validate(preset_data),
    )
