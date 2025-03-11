from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

import auth
from jlib.schemas.user import TokenSchema, UserCreateSchema, UserSchema, UserShowSchema
from jlib.services import BaseUserService
from jlib.utils.response import generate_responses
from services import UserService

router = APIRouter(prefix="/user")


@router.post(
    "/",
    response_model=UserShowSchema,
    status_code=status.HTTP_201_CREATED,
    responses=generate_responses(
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "User data invalid"),
        (status.HTTP_409_CONFLICT, "User already registered"),
    ),
)
async def register_user(
    user_create: UserCreateSchema,
    user_service: Annotated[BaseUserService, Depends(UserService)],
):
    return await user_service.register(user_create)


@router.get(
    "/{user_id}",
    response_model=UserShowSchema,
)
async def get_user_details(
    current_user: Annotated[UserSchema, Depends(auth.auth_utils.get_current_user)],
):
    return current_user


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[BaseUserService, Depends(UserService)],
) -> TokenSchema:
    return await auth.authenticate(
        user_service,
        form_data.username,
        form_data.password,
    )
