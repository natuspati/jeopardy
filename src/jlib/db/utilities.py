from jlib.db import DBSessionManager
from settings import settings

_default_db_manager = DBSessionManager(
    db_url=settings.db_url,
    db_echo=settings.db_echo,
    db_echo_pool=settings.db_echo_pool,
    db_isolation_level=settings.db_isolation_level,
    db_expire_on_commit=settings.db_expire_on_commit,
)


def get_db_manager() -> DBSessionManager:
    return _default_db_manager
