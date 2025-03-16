from abc import ABC

from jlib.schemas.pagination import PaginationSchema


class BaseLobbyService(ABC):
    async def get_lobbies(self, pagination: PaginationSchema):
        pass
