import logging

from sqlalchemy import bindparam, delete, insert, select

from jlib.dals import RelationalDAL
from jlib.errors.database import MissingRequiredDataInDBError
from models.category import CategoryModel
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel
from models.user import UserModel

_logger = logging.getLogger(__name__)

PRESETS = [
    {
        "id": 1,
        "name": "all by nurlat",
        "owner_id": 1,
        "categories": [
            {"preset_id": 1, "category_id": 1},
            {"preset_id": 1, "category_id": 2},
            {"preset_id": 1, "category_id": 3},
        ],
    },
    {
        "id": 2,
        "name": "no space by nurlat",
        "owner_id": 1,
        "categories": [
            {"preset_id": 2, "category_id": 1},
            {"preset_id": 2, "category_id": 3},
        ],
    },
    {
        "id": 3,
        "name": "all by john",
        "owner_id": 2,
        "categories": [
            {"preset_id": 3, "category_id": 1},
            {"preset_id": 3, "category_id": 2},
            {"preset_id": 3, "category_id": 3},
        ],
    },
]


async def create_presets(dal: RelationalDAL) -> None:
    await _check_required_entities_exist(dal)
    preset_categories = []
    for preset in PRESETS:
        preset_categories.extend(preset.pop("categories"))
    stmt = insert(PresetModel).values(PRESETS)
    await dal.execute(stmt)

    stmt = insert(PresetCategoryModel).values(preset_categories)
    await dal.execute(stmt)
    _logger.info("Finished creating categories")


async def remove_presets(dal: RelationalDAL) -> None:
    preset_ids = {p["id"] for p in PRESETS}
    stmt = delete(PresetModel).where(PresetModel.id.in_(preset_ids))
    await dal.execute(stmt)


async def _check_required_entities_exist(dal: RelationalDAL) -> None:
    owner_ids = {p["owner_id"] for p in PRESETS}
    stmt = select(UserModel).where(UserModel.id == bindparam("id"))
    for owner_id in owner_ids:
        owner = await dal.scalar(stmt, {"id": owner_id})
        if not owner:
            raise MissingRequiredDataInDBError(f"Owner {owner_id} not found.")
    category_ids = {
        category["category_id"] for preset in PRESETS for category in preset["categories"]
    }
    stmt = select(CategoryModel).where(CategoryModel.id == bindparam("id"))
    for category_id in category_ids:
        category = await dal.scalar(stmt, {"id": category_id})
        if not category:
            raise MissingRequiredDataInDBError(f"Category {category_id} not found.")
