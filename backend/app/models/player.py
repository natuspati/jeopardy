from typing import Optional

from app.models.core import CoreModel, IDModelMixin


class PlayerBase(CoreModel):
    user_id: Optional[str]
    lobby_id: Optional[str]
    score: int = 0
    name: Optional[str]


class PlayerCreate(PlayerBase):
    user_id = str
    lobby_id = str
    name = str


class PlayerUpdate(CoreModel):
    score: int


class PlayerInDB(IDModelMixin, PlayerBase):
    user_id: str
    lobby_id: str
    score: int
    name = str


class PlayerPublic(PlayerInDB):
    pass
