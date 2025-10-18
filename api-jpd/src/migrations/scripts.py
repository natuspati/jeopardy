import logging
import os

from alembic import command, config

from configs import settings

_logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg_path = os.path.join(os.path.dirname(__file__), "../alembic.ini")
    alembic_cfg = config.Config(alembic_cfg_path)
    _logger.info(f"Running migrations on database: {settings.db_url}")
    command.upgrade(config=alembic_cfg, revision="head", sql=False)
