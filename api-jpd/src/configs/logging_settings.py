import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"


class ProjectLoggerFilter(logging.Filter):
    """Filter that allows project logs at configured level, external logs at WARNING+"""

    def __init__(self) -> None:
        super().__init__()
        self.project_modules = {
            "api",
            "auth",
            "configs",
            "storages",
            "domains",
            "errors",
            "repositories",
            "services",
            "utils",
            "application",
            "lifespan",
            "main",
            "migrations",
        }
        self.project_log_level = getattr(logging, LOG_LEVEL)

    def filter(self, record: logging.LogRecord) -> bool:
        if any(record.name.startswith(module) for module in self.project_modules):
            return record.levelno >= self.project_log_level
        if record.name == "root":
            return record.levelno >= self.project_log_level
        return record.levelno >= logging.WARNING


def override_external_loggers() -> None:
    """Configure logging to set external loggers to WARNING level."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    handler.addFilter(ProjectLoggerFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
