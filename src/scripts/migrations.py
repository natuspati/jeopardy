import logging

from alembic import command, config

_logger = logging.getLogger(__name__)


def apply_migrations():
    alembic_cfg = config.Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    _logger.info("Finished applying migrations")
