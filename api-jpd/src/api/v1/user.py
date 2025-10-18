from typing import Annotated

from fastapi import APIRouter, Depends, status

from auth import authenticate_user, login_user
from schemas.token import TokenSchema
from schemas.user.base import BaseUserSchema, UserCreatePublicSchema
from schemas.user.nested import UserSchema
from services import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
    user_service: Annotated[UserService, Depends()],
):
    return await user_service.get_user(user_id=user.id)


@router.post("/token", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def login(
    token: Annotated[TokenSchema, Depends(login_user)],
):
    return token


@router.post("", response_model=BaseUserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreatePublicSchema,
    user_service: Annotated[UserService, Depends()],
):
    return await user_service.create_user(user)
