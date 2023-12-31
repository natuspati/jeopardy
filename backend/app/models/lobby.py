from __future__ import annotations
from typing import Optional

from app.models.core import IDModelMixin, UpdatedAtModelMixin, CoreModel


class LobbyBase(CoreModel):
    """
    All common characteristics of our Lobby resource
    """
    active: Optional[bool] = True


class LobbyCreate(LobbyBase):
    owner: str


class LobbyInDB(IDModelMixin, UpdatedAtModelMixin, LobbyBase):
    owner: str


class LobbyPublic(LobbyInDB):
    pass
