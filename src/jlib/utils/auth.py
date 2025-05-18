from datetime import datetime, timedelta

import bcrypt
import jwt

from jlib.errors.auth import ImproperTokenError
from jlib.schemas.user import TokenDataSchema
from settings import settings


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(
        password=password_byte_enc,
        hashed_password=hashed_password_byte_enc,
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(settings.timezone) + expires_delta
    else:
        expire = datetime.now(settings.timezone) + timedelta(
            minutes=settings.access_token_expire_min,
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> TokenDataSchema:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username = payload.get("sub")
    if username is None:
        raise ImproperTokenError("Username is missing")
    return TokenDataSchema(username=username)
