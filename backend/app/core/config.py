from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = "Jeopardy"
VERSION = "1.0.0"
API_PREFIX = "/api"

SECRET_KEY = config("SECRET_KEY", cast=Secret)

HOST_ADDRESS = config("HOST_ADDRESS", cast=str, default="localhost")

ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    cast=int,
    default=7 * 24 * 60  # one week
)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_AUDIENCE = config("JWT_AUDIENCE", cast=str, default="jeopardy:auth")
JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")

DATABASE_URL = config(
    "DATABASE_URL",
)
DATABASE_NAME = config(
    "DATABASE_NAME",
)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            
        },
    },
    "handlers": {
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "/tmp/debug.log",
            "level": "INFO",
        },
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "dev": {
            "handlers": ["console", "file"],
            "level": "DEBUG"
        },
    },
}
