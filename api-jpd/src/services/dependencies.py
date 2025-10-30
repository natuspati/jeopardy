from repositories import CategoryRepo, LobbyRepo
from services import CategoryService
from services.lobby import LobbyService
from storages import get_db_manager


def get_lobby_service() -> LobbyService:
    return LobbyService(
        lobby_repo=LobbyRepo(db_manager=get_db_manager()),
        category_service=get_category_service(),
    )


def get_category_service() -> CategoryService:
    return CategoryService(category_repo=CategoryRepo(db_manager=get_db_manager()))
