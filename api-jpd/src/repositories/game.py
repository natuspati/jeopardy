from repositories.mixins import RedisRepoMixin
from schemas.game import GameSchema


class GameRepo(RedisRepoMixin):
    NAME_SPACE = "game"

    async def get_game(self, game_id: int) -> GameSchema | None:
        game = await self.get(name="game", game_id=game_id)
        return GameSchema.model_validate_json(game) if game else None

    async def set_game(self, game: GameSchema) -> None:
        await self.set(name="game", value=game.model_dump_json(), game_id=game.id)
