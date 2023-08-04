from typing import Optional

from app.models.core import CoreModel


class PlayerBase(CoreModel):
    lobby_id: Optional[str]
    name: Optional[str]
    score: int = 0


class PlayerCreate(PlayerBase):
    lobby_id: str
    name: str


class PlayerUpdate(CoreModel):
    score: int


class PlayerInDB(PlayerBase):
    lobby_id: str
    name: str
    score: int


class PlayerPublic(PlayerInDB):
    pass
