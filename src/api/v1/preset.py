from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from auth import get_current_user
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
    PresetCreateShowSchema,
    PresetSchema,
    PresetUpdateSchema,
    PresetUpdateShowSchema,
)
from jlib.schemas.user import UserSchema
from jlib.services import BasePresetService
from jlib.utils.response import generate_responses
from services import PresetService

router = APIRouter(prefix="/preset", tags=["question"])


@router.get(
    "",
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
    """
    Get presets for the current user.
    """
    return await preset_service.get_presets(
        user_id=user.id,
        pagination=pagination,
    )


@router.get(
    "/{preset_id}",
    response_model=PresetSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the preset"),
        (status.HTTP_404_NOT_FOUND, "Preset not found"),
    ),
)
async def get_preset(
    preset_id: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    preset_service: Annotated[BasePresetService, Depends(PresetService)],
):
    """
    Get preset with categories and prompts.
    """
    return await preset_service.get_preset(preset_id=preset_id, user_id=user.id)


@router.post(
    "",
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
    """
    Create preset.
    """
    preset_data = {"owner_id": user.id} | (
        preset_create.model_dump() if preset_create else {}
    )
    return await preset_service.create_preset(
        preset=PresetCreateSchema.model_validate(preset_data),
    )


@router.patch(
    "/{preset_id}",
    response_model=PresetSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the preset"),
        (status.HTTP_404_NOT_FOUND, "Preset not found"),
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "Wrong data provided"),
    ),
)
async def update_preset(
    preset_id: int,
    preset_update: PresetUpdateShowSchema,
    user: Annotated[UserSchema, Depends(get_current_user)],
    preset_service: Annotated[BasePresetService, Depends(PresetService)],
):
    """
    Update preset name or its categories.
    """
    return await preset_service.update_preset(
        preset_update=PresetUpdateSchema(
            id=preset_id,
            owner_id=user.id,
            **preset_update.model_dump(exclude_unset=True, exclude_none=True),
        ),
    )


@router.delete(
    "/{preset_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the preset"),
    ),
)
async def delete_preset(
    preset_id: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    preset_service: Annotated[BasePresetService, Depends(PresetService)],
):
    """
    Delete preset.
    """
    await preset_service.delete_preset(preset_id=preset_id, user_id=user.id)
