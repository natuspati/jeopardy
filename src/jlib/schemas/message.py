from jlib.schemas.base import BaseSchema


class MessageSchema(BaseSchema):
    type: str
    content: str
