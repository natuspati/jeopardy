import logging

from sqlalchemy import bindparam, delete, insert, select

from jlib.dals.relational_dal import RelationalDAL
from jlib.errors.database import MissingRequiredDataInDBError
from models.category import CategoryModel
from models.user import UserModel

_logger = logging.getLogger(__name__)

CATEGORIES = [
    {
        "id": 1,
        "name": "Countries",
        "owner_id": 1,
    },
    {
        "id": 2,
        "name": "Space",
        "owner_id": 1,
    },
    {
        "id": 3,
        "name": "Movies",
        "owner_id": 2,
    },
]


async def create_categories(dal: RelationalDAL) -> None:
    await _check_required_users_exist(dal)
    await remove_categories(dal)
    stmt = insert(CategoryModel).values(CATEGORIES)
    await dal.execute(stmt)
    _logger.info("Finished creating categories")


async def remove_categories(dal: RelationalDAL) -> None:
    category_ids = {cat["id"] for cat in CATEGORIES}
    stmt = delete(CategoryModel).where(CategoryModel.id.in_(category_ids))
    await dal.execute(stmt)


async def _check_required_users_exist(dal: RelationalDAL) -> None:
    owner_ids = {cat["owner_id"] for cat in CATEGORIES}
    stmt = select(UserModel).where(UserModel.id == bindparam("id"))
    for owner_id in owner_ids:
        owner = await dal.scalar(stmt, {"id": owner_id})
        if not owner:
            raise MissingRequiredDataInDBError(f"Owner {owner_id} not found.")
