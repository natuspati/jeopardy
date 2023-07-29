from __future__ import annotations
from typing import Optional, Union, List
from enum import Enum

from app.models.core import IDModelMixin, CoreModel


class LobbyBase(CoreModel):
    """
    All common characteristics of our Lobby resource
    """
    
    name: Optional[str]
    finished: Optional[bool] = False
    

class LobbyCreate(LobbyBase):
    name: str
