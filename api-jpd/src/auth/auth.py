import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from auth.password import verify_password
from auth.scheme import basic_security, oauth2_scheme
from configs import settings
from errors.auth import ForbiddenError, UnauthorizedError
from schemas.token import TokenPayloadSchema, TokenSchema
from schemas.user.base import BaseUserSchema
from services import UserService


def check_basic_auth(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
) -> None:
    if not credentials:
        raise UnauthorizedError(
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    is_correct_username = secrets.compare_digest(
        credentials.username,
        settings.openapi_schema_user,
    )
    is_correct_password = secrets.compare_digest(
        credentials.password,
        settings.openapi_schema_pass,
    )

    if not (is_correct_username and is_correct_password):
        raise ForbiddenError("Failed to verify credentials")


async def authenticate_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends()],
) -> BaseUserSchema:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise UnauthorizedError("Failed to verify credentials")
        token_payload = TokenPayloadSchema(username=username)
    except InvalidTokenError as error:
        raise UnauthorizedError("Failed to verify credentials") from error
    user = await user_service.get_user(username=token_payload.username, extra=False)
    if user is None:
        raise UnauthorizedError("Failed to verify credentials")
    return user


async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends()],
) -> TokenSchema:
    user = await user_service.get_user(
        username=form_data.username,
        extra=False,
    )
    if not user or not verify_password(form_data.password, user.password):
        raise UnauthorizedError("Invalid username or password")

    access_token_expires = timedelta(seconds=settings.token_expiration_sec)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires,
    )
    return TokenSchema(access_token=access_token, token_type="bearer")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.token_expiration_sec)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt
