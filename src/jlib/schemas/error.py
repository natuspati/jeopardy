from jlib.schemas.base import BaseSchema


class ErrorSchema(BaseSchema):
    detail: str
