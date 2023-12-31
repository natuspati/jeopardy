from datetime import datetime, timedelta
from typing import List

from pydantic import EmailStr

from app.core.config import JWT_AUDIENCE, ACCESS_TOKEN_EXPIRE_MINUTES, HOST_ADDRESS
from app.models.core import CoreModel


class JWTMeta(CoreModel):
    iss: str = HOST_ADDRESS
    aud: str = JWT_AUDIENCE
    iat: float = datetime.timestamp(datetime.utcnow())
    exp: float = datetime.timestamp(datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


class JWTCreds(CoreModel):
    """How we'll identify users"""

    sub: EmailStr
    username: str
    scopes: List[str] = []


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """

    pass


class AccessToken(CoreModel):
    access_token: str
    token_type: str
    