import asyncio
import logging

from jlib.dals.relational_dal import RelationalDAL
from jlib.db.utilities import get_db_manager
from models import import_models
from scripts.mock_data.categories import create_categories
from scripts.mock_data.prompts import create_prompts
from scripts.mock_data.users import create_users

_logger = logging.getLogger(__name__)


def apply_mock_data() -> None:
    asyncio.run(_apply_mock_data())
    _logger.info("Finished applying mock data")


async def _apply_mock_data() -> None:
    dal = RelationalDAL(get_db_manager())
    await create_users(dal)
    await create_categories(dal)
    await create_prompts(dal)
