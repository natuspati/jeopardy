from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from repositories import GameRepo, UserRepo
from services import UserService
from services.game import GameService
from storages import get_db_manager, get_redis_manager


@asynccontextmanager
async def get_user_service() -> AsyncGenerator[UserService, None]:
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        yield UserService(user_repo=UserRepo(session=session))


@asynccontextmanager
async def get_game_service() -> AsyncGenerator[GameService, None]:
    async with get_user_service() as user_service:
        yield GameService(
            game_repo=GameRepo(redis_manager=get_redis_manager()),
            user_service=user_service,
        )
