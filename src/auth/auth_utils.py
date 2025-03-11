from typing import Annotated

from fastapi import Depends
from jwt import InvalidTokenError

from auth.scheme import oauth2_scheme
from jlib.errors.auth import ImproperTokenError, UnauthorizedError
from jlib.schemas.user import TokenSchema, UserSchema
from jlib.services import BaseUserService
from jlib.utils.auth import create_access_token, decode_token, verify_password
from services import UserService


async def authenticate(
    user_service: BaseUserService,
    username: str,
    password: str,
) -> TokenSchema:
    user = await user_service.get_by_username(username)
    if not user:
        raise UnauthorizedError(f"User {username} not found")

    if not verify_password(password, user.password):
        raise UnauthorizedError("Invalid password")

    access_token = create_access_token(
        data={"sub": user.username},
    )
    return TokenSchema(access_token=access_token, token_type="bearer")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[BaseUserService, Depends(UserService)],
) -> UserSchema:
    try:
        token_data = decode_token(token)
    except (ImproperTokenError, InvalidTokenError) as err:
        raise UnauthorizedError("Invalid token") from err
    user = await user_service.get_by_username(username=token_data.username)
    if not user:
        raise UnauthorizedError("User not found")
    return user
