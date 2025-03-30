import uuid

from jlib.enums import LobbyMemberTypeEnum
from jlib.schemas.base import BaseSchema


class PlayerSchema(BaseSchema):
    user_id: int
    username: str
    lobby_id: uuid.UUID
    score: int | None = None
    type: LobbyMemberTypeEnum
