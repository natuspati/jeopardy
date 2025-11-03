import logging
from typing import Any
from urllib.parse import parse_qs

import socketio

from auth.auth import authenticate_user
from enums.game import GameStateEnum
from enums.player import LeadStateEnum, PlayerStateEnum
from errors.auth import ForbiddenError, UnauthorizedError
from errors.handlers import handle_event_errors
from errors.request import BadRequestError, NotFoundError
from schemas.game import (
    GameEventSchema,
    GamePayloadSchema,
    GameSchema,
    GameSessionShema,
    GameUpdateSchema,
)
from schemas.game_event.connect import ConnectEventSchema, DisconnectEventSchema
from schemas.game_event.error import GameErrorEvent, GameErrorPayloadSchema
from schemas.game_event.start import GameStartedEvent
from schemas.player import PlayerUpdateSchema
from schemas.user.base import BaseUserSchema
from services.dependencies import get_game_service, get_user_service

_logger = logging.getLogger(__name__)


class GameNamespace(socketio.AsyncNamespace):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._game_service = get_game_service()
        self._user_service = get_user_service()

    @handle_event_errors(emit_error=True, return_value=False)
    async def on_connect(self, sid: str, environ: dict[str, Any], auth: dict[str, Any]) -> bool:
        try:
            user = await self._authenticate(auth)
        except UnauthorizedError as error:
            _logger.info(f"Client {sid} rejected: {error.detail}")
            await self._emit_error(error.detail, room=sid)
            return False

        try:
            game_id = self._get_game_from_environment(environ)
        except BadRequestError as error:
            _logger.info(f"Client {sid} rejected: {error.detail}")
            await self._emit_error(error.detail, room=sid)
            return False

        try:
            game = await self._game_service.get_game(game_id)
        except NotFoundError as error:
            _logger.info(f"Client {sid} rejected: no lobby with ID {game_id}")
            await self._emit_error(error.detail, room=sid)
            return False

        try:
            game = await self._join_game(sid=sid, game=game, user=user)
        except ForbiddenError as error:
            _logger.info(f"Client {sid} rejected: {error.detail}")
            await self._emit_error(error.detail, room=sid)
            return False

        await self._emit_game_event(ConnectEventSchema, game=game, skip_sid=sid)
        _logger.info(f"Client {sid} connected to game {game.id}")
        return True

    @handle_event_errors(emit_error=False, return_value=None)
    async def on_disconnect(self, sid: str, reason: str) -> None:
        session = await self._get_session(sid)
        if session.is_lead:
            game = await self._update_game(
                session.game_id,
                GameUpdateSchema(lead_state=LeadStateEnum.DISCONNECTED),
            )
        else:
            game = await self._update_game(
                session.game_id,
                GameUpdateSchema(
                    update_players={
                        session.player_id: PlayerUpdateSchema(state=PlayerStateEnum.DISCONNECTED),
                    },
                ),
            )

        await self._emit_game_event(DisconnectEventSchema, game, skip_sid=sid)
        _logger.info(f"Client {sid} disconnected, reason: {reason}.")

    @handle_event_errors(emit_error=True, return_value=None)
    async def on_game_start(self, sid: str) -> None:
        session = await self._get_session(sid)

        if not session.is_lead:
            await self._emit_error("Only lead is authorized to start game", room=sid)
            return

        game = await self._get_game(session.game_id)

        if game.state is not GameStateEnum.BEFORE_START:
            await self._emit_error("Game has been already started", room=sid)
            return

        if not game.valid_num_players:
            await self._emit_error("Not valid number of players", room=sid)
            return

        game = await self._update_game(
            session.game_id,
            GameUpdateSchema(state=GameStateEnum.SELECT_PLAYER),
        )
        await self._emit_game_event(GameStartedEvent, game)

    async def _authenticate(self, auth: dict[str, Any]) -> BaseUserSchema:
        token = auth.get("token")
        if not token:
            raise UnauthorizedError("Missing authorization token")
        return await authenticate_user(token=token, user_service=self._user_service)

    async def _join_game(
        self,
        *,
        sid: str,
        game: GameSchema,
        user: BaseUserSchema,
    ) -> GameSchema:
        is_lead = False

        if game.player_map.get(user.id):
            game = await self._rejoin_as_player(game, user)
        elif user.id == game.lead.id:
            game = await self._rejoin_as_lead(game)
            is_lead = True
        else:
            game = await self._join_as_new_player(game, user)

        await self._set_session(sid=sid, game_id=game.id, player_id=user.id, is_lead=is_lead)
        await self.enter_room(sid=sid, room=self._get_room(game.id))
        return game

    async def _rejoin_as_player(self, game: GameSchema, user: BaseUserSchema) -> GameSchema:
        player = game.player_map[user.id]
        if player.state is PlayerStateEnum.CONNECTED:
            raise ForbiddenError(f"Player {player.id} is already connected")
        elif player.state is PlayerStateEnum.BANNED:
            raise ForbiddenError(f"Player {player.id} is banned")
        else:
            return await self._update_game(
                game.id,
                GameUpdateSchema(
                    update_players={player.id: PlayerUpdateSchema(state=PlayerStateEnum.CONNECTED)},
                ),
            )

    async def _rejoin_as_lead(self, game: GameSchema) -> GameSchema:
        if game.lead.state is LeadStateEnum.CONNECTED:
            raise ForbiddenError(f"Lead {game.lead.id} is already connected")
        else:
            game = await self._update_game(
                game.id,
                GameUpdateSchema(lead_state=LeadStateEnum.CONNECTED),
            )
            return game

    async def _join_as_new_player(self, game: GameSchema, user: BaseUserSchema) -> GameSchema:
        if game.state is GameStateEnum.BEFORE_START:
            return await self._update_game(game.id, GameUpdateSchema(add_player_ids=[user.id]))
        else:
            raise ForbiddenError(f"Game {game.id} has been started")

    async def _get_game(self, game_id: int) -> GameSchema:
        return await self._game_service.get_game(game_id)

    async def _update_game(self, game_id: int, game_update: GameUpdateSchema) -> GameSchema:
        return await self._game_service.update_game(game_id, game_update=game_update)

    async def _get_session(self, sid: str) -> GameSessionShema:
        async with self.session(sid) as session:
            game_session: dict = session.get("game_session")
            if not game_session:
                raise NotFoundError(f"Client {sid} has no game session")
            return GameSessionShema.model_validate(game_session)

    async def _set_session(self, *, sid: str, game_id: int, player_id: int, is_lead: bool) -> None:
        async with self.session(sid) as session:
            session["game_session"] = GameSessionShema(
                game_id=game_id,
                player_id=player_id,
                is_lead=is_lead,
            ).model_dump(mode="json")

    async def _emit_game_event(
        self,
        schema: type[GameEventSchema],
        game: GameSchema,
        *,
        room: str | int | None = None,
        skip_sid: str | list[str] | None = None,
    ) -> None:
        if room is None:
            room = self._get_room(game.id)
        await self._emit(schema(payload=GamePayloadSchema(game=game)), room=room, skip_sid=skip_sid)

    async def _emit_error(self, detail: str, *, room: str | int | None = None) -> None:
        await self._emit(
            GameErrorEvent(payload=GameErrorPayloadSchema(detail=detail)),
            room=room,
        )

    async def _emit(
        self,
        event: GameEventSchema,
        *,
        room: str | int | None = None,
        skip_sid: str | list[str] | None = None,
    ) -> None:
        await self.emit(
            event=event.name,
            data=event.payload.model_dump() if event.payload else None,
            room=room,
            skip_sid=skip_sid,
        )

    @classmethod
    def _get_room(cls, game_id: int) -> str:
        return f"game:id={game_id}"

    @classmethod
    def _get_game_from_environment(cls, environ: dict[str, Any]) -> int:
        query_string = environ.get("QUERY_STRING")
        if not query_string:
            raise BadRequestError("No query parameters provided")

        query_params = parse_qs(query_string)
        lobby_ids = query_params.get("lobby_id")
        if not lobby_ids or len(lobby_ids) > 1:
            raise BadRequestError("Invalid lobby_id in query parameters")

        try:
            lobby_id = int(lobby_ids[0])
        except ValueError as error:
            raise BadRequestError(f"Invalid lobby ID {lobby_ids[0]}") from error

        return lobby_id
