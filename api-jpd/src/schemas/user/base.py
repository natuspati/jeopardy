from pydantic import BaseModel, Field

from schemas.base import NoTZDateTime


class BaseUserSchema(BaseModel):
    id: int
    username: str
    created_at: NoTZDateTime
    password: str = Field(exclude=True)


class UserCreatePublicSchema(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=3, max_length=16)


class UserCreateSchema(BaseModel):
    username: str
    password: str
