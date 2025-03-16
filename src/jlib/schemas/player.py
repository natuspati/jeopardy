from jlib.enums import LobbyMemberTypeEnum
from jlib.schemas.base import BaseSchema


class PlayerSchema(BaseSchema):
    user_id: int
    username: str
    score: int | None = None
    type: LobbyMemberTypeEnum
