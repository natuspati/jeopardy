from typing import Literal

import pytz
import sqlalchemy
from pydantic_settings import BaseSettings, SettingsConfigDict

from jlib.enums import AppEnvironmentEnum
from jlib.types.database import ISOLATION_LEVEL_TYPE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="JEOPARDY_",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
        env_parse_none_str="null",
    )

    # Uvicorn
    host: str = "0.0.0.0"
    port: int = 8000
    workers_count: int = 1
    reload: bool = True

    # App environment
    app_environment: Literal["test", "local", "dev", "prod"] = "local"
    app_name: str = "Jeopardy"
    secret_key: str = "jeopardy"

    # Authentication
    algorithm: str = "HS256"
    token_type: str = "bearer"
    access_token_expire_min: int = 60  # in minutes

    # Pagination
    page_size: int = 50
    max_query_limit: int = 100

    # Variables for the database
    db_driver: str = "postgresql+asyncpg"
    db_host: str | None = "localhost"
    db_port: int | None = 5432
    db_user: str | None = "jeopardy"
    db_pass: str | None = "jeopardy"
    db_name: str | None = "jeopardy"
    db_echo: bool = False
    db_echo_pool: bool = False
    db_isolation_level: ISOLATION_LEVEL_TYPE = "READ COMMITTED"
    db_expire_on_commit: bool = False

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_pass: str | None = None
    redis_socket_timeout: int = 3
    redis_default_expiration_time: int | None = 60 * 60  # 1 hour
    redis_encoding: str = "utf-8"
    redis_namespace: str = "jeopardy_"
    redis_empty_value: str = "not_found"

    # Timezone as pytz timezone string
    pytz_timezone: str = "Etc/GMT-5"

    @property
    def db_url(self) -> sqlalchemy.URL:
        return sqlalchemy.URL.create(
            drivername=self.db_driver,
            host=self.db_host,
            port=self.db_port,
            username=self.db_user,
            password=self.db_pass,
            database=self.db_name,
        )

    @property
    def environment(self) -> AppEnvironmentEnum:
        """
        Application environment.

        :return: application environment
        """
        return AppEnvironmentEnum(self.app_environment)

    @property
    def timezone(self) -> pytz.timezone:
        """
        Get current timezone.

        :return: timezone as `pytz.timezone`
        """
        return pytz.timezone(self.pytz_timezone)


settings = Settings()
