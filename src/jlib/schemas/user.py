from jlib.schemas.base import BaseSchema, OneFieldSetSchemaMixin


class UserSchema(BaseSchema):
    id: int
    username: str
    password: str
    deleted: bool


class UserCreateSchema(BaseSchema):
    username: str
    password: str


class UserUpdateSchema(BaseSchema, OneFieldSetSchemaMixin):
    username: str | None = None
    password: str | None = None
    deleted: bool | None = None


class UserShowSchema(BaseSchema):
    id: int
    username: str


class TokenSchema(BaseSchema):
    access_token: str
    token_type: str


class TokenDataSchema(BaseSchema):
    username: str | None = None
