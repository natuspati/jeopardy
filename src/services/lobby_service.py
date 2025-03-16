from typing import Annotated

from fastapi import Depends

from dals import LobbyDAL
from jlib.dals import BaseLobbyDAL
from jlib.schemas.lobby import LobbySchema
from jlib.schemas.pagination import PaginationSchema
from jlib.services import BaseLobbyService
from jlib.utils.pagination import check_pagination


class LobbyService(BaseLobbyService):
    def __init__(self, lobby_dal: Annotated[BaseLobbyDAL, Depends(LobbyDAL)]):
        self._lobby_dal = lobby_dal

    async def get_lobbies(self, pagination: PaginationSchema) -> list[LobbySchema]:
        check_pagination(pagination)
        return await self._lobby_dal.select(
            offset=pagination.offset,
            limit=pagination.limit,
        )

    async def create_lobby(self):
        pass
