from repositories import CategoryRepo, GameRepo, UserRepo
from services import UserService
from services.category import CategoryService
from services.game import GameService
from storages import get_db_manager, get_db_session, get_redis_manager


async def get_category_service() -> CategoryService:
    async with get_db_session(get_db_manager()) as session:
        return CategoryService(category_repo=CategoryRepo(session=session))


async def get_user_service() -> UserService:
    async with get_db_session(get_db_manager()) as session:
        return UserService(
            user_repo=UserRepo(session=session),
        )


async def get_game_service() -> GameService:
    async with get_user_service() as user_service:
        return GameService(
            game_repo=GameRepo(redis_manager=get_redis_manager()),
            user_service=user_service,
        )
