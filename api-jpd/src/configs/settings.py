from typing import Literal

import sqlalchemy
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
        env_parse_none_str="null",
    )

    # Uvicorn
    host: str = "0.0.0.0"
    port: int = 8080
    workers_count: int = 1
    reload: bool = True

    # App environment
    environment: Literal["test", "local", "prod"] = "local"
    name: str = "Jeopardy API"
    version: str = "0.0.1"

    # Authentication
    openapi_schema_user: str = "jeopardy"
    openapi_schema_pass: str = "jeopardy"

    # Variables for database
    db_apply_migrations: bool = False
    db_driver: str = "postgresql+asyncpg"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "jeopardy"
    db_pass: str = "jeopardy"
    db_name: str = "jeopardy"
    db_echo: bool = False
    db_echo_pool: bool = False
    db_isolation_level: str = "READ COMMITTED"
    db_rollback: bool = False
    db_expire_on_commit: bool = False
    db_conn_pool_size: int = 10
    db_conn_pool_recycle: int = 3600

    # Variables for redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_decode_responses: bool = True
    redis_socket_timeout: float | None = None
    redis_max_connections: int = 10
    redis_expiration_sec: int = 7 * 24 * 60 * 60  # 7 days in seconds

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


settings = Settings()
