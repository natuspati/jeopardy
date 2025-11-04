from typing import Annotated

from fastapi import Depends

from constants import UnsetSentinel
from enums.game import GameStateEnum
from enums.player import PlayerStateEnum
from enums.prompt import PromptStateEnum
from errors.request import BadRequestError, NotFoundError
from repositories import GameRepo
from schemas.category.nested import CategoryInGameSchema
from schemas.game import GameSchema, GameUpdateSchema
from schemas.lobby.nested import LobbySchema
from schemas.player import LeadSchema, PlayerSchema
from services.user import UserService


class GameService:
    def __init__(
        self,
        game_repo: Annotated[GameRepo, Depends()],
        user_service: Annotated[UserService, Depends()],
    ):
        self._game_repo = game_repo
        self._user_service = user_service

    async def get_game(self, game_id: int) -> GameSchema:
        game = await self._game_repo.get_game(game_id)
        if not game:
            raise NotFoundError(f"Game with ID {game_id} not found")
        return game

    async def create_game(self, lobby: LobbySchema) -> GameSchema:
        if not lobby.is_valid:
            raise BadRequestError(f"Lobby ID {lobby.id} is not valid")

        game = GameSchema(
            id=lobby.id,
            state=GameStateEnum.BEFORE_START,
            lead=LeadSchema(**lobby.host.model_dump()),
            players=[],
            categories=[CategoryInGameSchema(**cat.model_dump()) for cat in lobby.categories],
        )
        await self._game_repo.set_game(game)
        return game

    async def update_game(self, game_id: int, game_update: GameUpdateSchema) -> GameSchema:
        game = await self.get_game(game_id)
        updated_game = game.model_copy(deep=True)

        self._change_state(game_update, game)
        self._select_player(game_update, game)
        self._select_prompt(game_update, game)

        self._update_lead(game_update, game)
        self._update_players(game_update, game)
        await self._add_new_players(game_update, game)

        await self._game_repo.set_game(game)
        return updated_game

    async def _add_new_players(
        self,
        game_update: GameUpdateSchema,
        game: GameSchema,
    ) -> None:
        if not game_update.add_player_ids:
            return

        unique_player_ids = set(game_update.add_player_ids)
        existing_player_ids = unique_player_ids & set(game.player_map.keys())
        if existing_player_ids:
            raise BadRequestError(f"Players with IDs {existing_player_ids} already exist")

        users = await self._user_service.get_users(*unique_player_ids)
        fetched_user_ids = {user.id for user in users}
        missing_player_ids = unique_player_ids - fetched_user_ids
        if missing_player_ids:
            raise BadRequestError(f"Players with IDs {missing_player_ids} are missing")

        game.players.extend([PlayerSchema(**user.model_dump()) for user in users])

    @classmethod
    def _change_state(cls, game_update: GameUpdateSchema, game: GameSchema) -> None:
        if game_update.state:
            game.state = game_update.state

    @classmethod
    def _update_lead(cls, game_update: GameUpdateSchema, game: GameSchema) -> None:
        if game_update.lead_state:
            game.lead.state = game_update.lead_state

    @classmethod
    def _update_players(cls, game_update: GameUpdateSchema, game: GameSchema) -> None:
        if not game_update.update_players:
            return

        unique_player_ids = set(game_update.update_players.keys())
        missing_player_ids = unique_player_ids - set(game.player_map.keys())
        if missing_player_ids:
            raise BadRequestError(f"Players with IDs {missing_player_ids} not found")

        for player_id, player_update in game_update.update_players.items():
            if player_update.state:
                game.player_map[player_id].state = player_update.state
            if player_update.score:
                game.player_map[player_id].score = player_update.score

    @classmethod
    def _select_player(cls, game_update: GameUpdateSchema, game: GameSchema) -> None:
        player_id = game_update.selected_player_id
        if player_id is UnsetSentinel:
            return

        if player_id == game.selected_player_id:
            raise BadRequestError("Selected player matches existing selection")

        if player_id not in game.player_map:
            raise BadRequestError(f"Player with ID {player_id} not found")

        game.selected_player.state = PlayerStateEnum.CONNECTED

        if player_id is not None:
            game.player_map[player_id].state = PlayerStateEnum.SELECTED

    @classmethod
    def _select_prompt(cls, game_update: GameUpdateSchema, game: GameSchema) -> None:
        prompt_id = game_update.selected_prompt_id
        if prompt_id is UnsetSentinel:
            return

        if prompt_id == game.selected_prompt_id:
            raise BadRequestError("Selected prompt matches existing selection")

        if prompt_id not in game.prompt_map:
            raise BadRequestError(f"Prompt with ID {prompt_id} not found")

        game.selected_prompt.state = PromptStateEnum.NOT_SELECTED

        if prompt_id is not None:
            game.prompt_map[prompt_id].state = PromptStateEnum.NOT_SELECTED
