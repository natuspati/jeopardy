from typing import Type

import jwt
import bcrypt
from datetime import datetime, timedelta

from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from app.core.config import (
    SECRET_KEY, HOST_ADDRESS, JWT_AUDIENCE, ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM
)

from app.models.token import JWTMeta, JWTCreds, JWTPayload
from app.models.user import UserPasswordUpdate, UserBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthException(BaseException):
    """
    Custom auth exception that can be modified later on.
    """
    pass


class AuthService:
    def create_salt_and_hashed_password(self, *, plaintext_password: str) -> UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt)
        return UserPasswordUpdate(salt=salt, password=hashed_password)
    
    @staticmethod
    def generate_salt() -> str:
        return bcrypt.gensalt().decode()
    
    @staticmethod
    def hash_password(*, password: str, salt: str) -> str:
        return pwd_context.hash(password + salt)
    
    @staticmethod
    def verify_password(*, password: str, salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(password + salt, hashed_pw)
    
    @staticmethod
    def create_access_token_for_user(
            *,
            user: Type[UserBase],
            secret_key: str = str(SECRET_KEY),
            host_address: str = HOST_ADDRESS,
            audience: str = JWT_AUDIENCE,
            expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str | None:
        if not user or not isinstance(user, UserBase):
            return None
        
        jwt_meta = JWTMeta(
            iss=host_address,
            aud=audience,
            iat=datetime.timestamp(datetime.utcnow()),
            exp=datetime.timestamp(datetime.utcnow() + timedelta(minutes=expires_in)),
        )
        jwt_creds = JWTCreds(sub=user.email, username=user.username)
        token_payload = JWTPayload(
            **jwt_meta.model_dump(),
            **jwt_creds.model_dump(),
        )
        
        access_token = jwt.encode(token_payload.model_dump(), secret_key, algorithm=JWT_ALGORITHM)
        return access_token
    
    @staticmethod
    def get_username_from_token(
            *,
            token: str,
            secret_key: str
    ) -> str:
        try:
            decoded_token = jwt.decode(
                token,
                str(secret_key),
                issuer=HOST_ADDRESS,
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM]
            )
            payload = JWTPayload(**decoded_token)
        except (jwt.PyJWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.username
