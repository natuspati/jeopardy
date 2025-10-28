from pydantic import BaseModel

from enums.player import PlayerStateEnum


class PlayerSchema(BaseModel):
    id: int
    username: str
    state: PlayerStateEnum = PlayerStateEnum.ACTIVE
    score: int = 0


class LeadSchema(BaseModel):
    id: int
    username: str
