import logging

from sqlalchemy import bindparam, delete, insert, select

from jlib.dals import RelationalDAL
from jlib.errors.database import MissingRequiredDataInDBError
from models.category import CategoryModel
from models.prompt import PromptModel
from scripts.mock_data.prompts.prompts_for_countries_category import COUNTRY_PROMPTS
from scripts.mock_data.prompts.prompts_for_movies_category import MOVIES_PROMPTS
from scripts.mock_data.prompts.prompts_for_space_category import SPACE_PROMPTS

_logger = logging.getLogger(__name__)
ALL_PROMPTS = COUNTRY_PROMPTS + SPACE_PROMPTS + MOVIES_PROMPTS


async def create_prompts(dal: RelationalDAL) -> None:
    await _check_required_categories_exist(dal)
    stmt = insert(PromptModel).values(ALL_PROMPTS)
    await dal.execute(stmt)
    _logger.info("Finished creating prompts")


async def remove_prompts(dal: RelationalDAL) -> None:
    prompt_ids = {prompt["id"] for prompt in ALL_PROMPTS}
    stmt = delete(PromptModel).where(PromptModel.id.in_(prompt_ids))
    await dal.execute(stmt)


async def _check_required_categories_exist(dal: RelationalDAL) -> None:
    category_ids = {prompt["category_id"] for prompt in ALL_PROMPTS}
    stmt = select(CategoryModel).where(CategoryModel.id == bindparam("id"))
    for category_id in category_ids:
        category = await dal.scalar(stmt, {"id": category_id})
        if not category:
            raise MissingRequiredDataInDBError(f"Category {category_id} does not exist")
