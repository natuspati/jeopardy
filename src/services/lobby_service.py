import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket

from dals import LobbyDAL, PresetDAL
from jlib.dals import BaseLobbyDAL, BasePresetDAL
from jlib.enums import LobbyMemberTypeEnum
from jlib.errors.request import BadRequestError
from jlib.errors.resource import ResourceNotFoundError
from jlib.schemas.category import CategoryInGameSchema
from jlib.schemas.lobby import (
    BasicLobbySchema,
    LobbyCreateSchema,
    LobbyCreateShowSchema,
    LobbyJoinSchema,
    LobbySchema,
    LobbyUpdateSchema,
    PaginatedBasicLobbySchema,
)
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.player import PlayerSchema
from jlib.schemas.user import UserSchema
from jlib.services import BaseGameFlowService, BaseLobbyService
from jlib.utils.app import get_app
from jlib.utils.pagination import check_pagination
from services.flow_service import GameFlowService


class LobbyService(BaseLobbyService):
    def __init__(
        self,
        app: Annotated[FastAPI, Depends(get_app)],
        lobby_dal: Annotated[BaseLobbyDAL, Depends(LobbyDAL)],
        preset_dal: Annotated[BasePresetDAL, Depends(PresetDAL)],
        flow_service: Annotated[BaseGameFlowService, Depends(GameFlowService)],
    ):
        self._app = app
        self._lobby_dal = lobby_dal
        self._preset_dal = preset_dal
        self._flow_service = flow_service

    async def get_lobbies(
        self,
        pagination: PaginationSchema,
    ) -> PaginatedBasicLobbySchema:
        check_pagination(pagination)
        lobbies = await self._lobby_dal.select(
            offset=pagination.offset,
            limit=pagination.limit,
        )
        basic_lobbies = [
            BasicLobbySchema(id=lob.id, state=lob.state, num_players=len(lob.players))
            for lob in lobbies
        ]
        return PaginatedBasicLobbySchema.paginate(
            items=basic_lobbies,
            pagination=pagination,
        )

    async def create_lobby(
        self,
        user: UserSchema,
        lobby_create: LobbyCreateShowSchema,
    ) -> LobbyJoinSchema:
        preset = await self._preset_dal.select_by_id(lobby_create.preset_id)
        if not preset:
            raise BadRequestError(
                f"Preset with id {lobby_create.preset_id} does not exist"
            )
        lobby_id = self._create_lobby_id()
        lobby = await self._lobby_dal.create(
            LobbyCreateSchema(
                id=lobby_id,
                players=[
                    PlayerSchema(
                        user_id=user.id,
                        username=user.username,
                        lobby_id=lobby_id,
                        type=LobbyMemberTypeEnum.LEAD,
                    ),
                ],
                categories=[
                    CategoryInGameSchema(**cat.model_dump())
                    for cat in preset.categories
                ],
            )
        )
        return LobbyJoinSchema(
            join_url=self._app.url_path_for("join_lobby", lobby_id=lobby_id),
            num_players=len(lobby.players),
            **lobby.model_dump(),
        )

    async def join_lobby(
        self,
        lobby_id: str,
        user: UserSchema,
        connection: WebSocket,
    ) -> None:
        player = await self._get_player(lobby_id, user)
        await self._flow_service.play(player, connection)

    async def _get_player(self, lobby_id: str, user: UserSchema) -> PlayerSchema:
        lobby = await self._lobby_dal.select_by_id(lobby_id)
        if not lobby:
            raise ResourceNotFoundError(f"Lobby with id {lobby_id} does not exist")
        try:
            return lobby[user.id]
        except KeyError:
            return await self._add_player(user, lobby)

    async def _add_player(self, user: UserSchema, lobby: LobbySchema) -> PlayerSchema:
        player = PlayerSchema(
            user_id=user.id,
            username=user.username,
            lobby_id=lobby.id,
            type=LobbyMemberTypeEnum.PLAYER,
        )
        lobby.players.append(player)
        await self._lobby_dal.update(
            LobbyUpdateSchema(
                id=lobby.id,
                players=lobby.players,
            )
        )
        return player

    @classmethod
    def _create_lobby_id(cls, as_string: bool = False) -> uuid.UUID | str:
        lobby_id = uuid.uuid4()
        return lobby_id.hex if as_string else lobby_id
