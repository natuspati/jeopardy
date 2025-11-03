from repositories import CategoryRepo, GameRepo, UserRepo
from services import UserService
from services.category import CategoryService
from services.game import GameService
from storages import get_db_manager, get_redis_manager


def get_category_service() -> CategoryService:
    return CategoryService(category_repo=CategoryRepo(db_manager=get_db_manager()))


def get_user_service() -> UserService:
    return UserService(
        user_repo=UserRepo(db_manager=get_db_manager()),
    )


def get_game_service() -> GameService:
    return GameService(
        game_repo=GameRepo(redis_manager=get_redis_manager()),
        user_service=get_user_service(),
    )
