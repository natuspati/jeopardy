import logging

from sqlalchemy import delete, insert

from jlib.dals import RelationalDAL
from jlib.utils.auth import hash_password
from models.user import UserModel

_logger = logging.getLogger(__name__)

USERS = [
    {
        "id": 1,
        "username": "nurlat",
        "password": hash_password("nurlat"),
        "deleted": False,
    },
    {
        "id": 2,
        "username": "john",
        "password": hash_password("john"),
        "deleted": False,
    },
    {
        "id": 3,
        "username": "alice",
        "password": hash_password("alice"),
        "deleted": False,
    },
]


async def create_users(dal: RelationalDAL) -> None:
    stmt = insert(UserModel).values(USERS)
    await dal.execute(stmt)
    _logger.info("Finished creating users")


async def remove_users(dal: RelationalDAL) -> None:
    user_ids = {u["id"] for u in USERS}
    stmt = delete(UserModel).where(UserModel.id.in_(user_ids))
    await dal.execute(stmt)
