from typing import Optional

from pydantic import Field, EmailStr

from app.models.core import CoreModel, IDModelMixin, UpdatedAtModelMixin
from app.models.token import AccessToken


class UserBase(CoreModel):
    """
    Leaving off password and salt from base model
    """
    username: str
    email: Optional[str]
    email_verified: Optional[bool] = False
    disabled: Optional[bool] = False


class UserCreate(CoreModel):
    """
    Email, username, and password are required for registering a new user
    """
    email: EmailStr
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$"
    )
    password: str = Field(
        min_length=7,
        max_length=100
    )


class UserUpdate(CoreModel):
    """
    Users are allowed to update their email and username
    """
    email: Optional[str] = None
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$"
    )


class UserPasswordUpdate(CoreModel):
    """
    Users can change their password
    """
    
    password: str = Field(
        min_length=7,
        max_length=100
    )
    salt: str


class UserInDB(IDModelMixin, UpdatedAtModelMixin, UserBase):
    """
    Add in id, created_at, updated_at, and user's password and salt
    """
    
    password: str = Field(
        min_length=7,
        max_length=100
    )
    salt: str


class UserPublic(IDModelMixin, UpdatedAtModelMixin, UserBase):
    access_token: Optional[AccessToken]
    
