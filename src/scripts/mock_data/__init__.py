import asyncio
import logging

from jlib.dals import RelationalDAL
from jlib.db import get_db_manager
from models import import_models
from scripts.mock_data.categories import create_categories, remove_categories
from scripts.mock_data.presets import create_presets, remove_presets
from scripts.mock_data.prompts import create_prompts, remove_prompts
from scripts.mock_data.users import create_users, remove_users

_logger = logging.getLogger(__name__)


def apply_mock_data() -> None:
    asyncio.run(_apply_mock_data())
    _logger.info("Finished applying mock data")


async def _apply_mock_data() -> None:
    dal = RelationalDAL(get_db_manager())
    await remove_presets(dal)
    await remove_prompts(dal)
    await remove_categories(dal)
    await remove_users(dal)
    await create_users(dal)
    await create_categories(dal)
    await create_prompts(dal)
    await create_presets(dal)
