from typing import Literal

from pydantic import BaseModel

IsolationLevelType = Literal[
    "SERIALIZABLE",
    "REPEATABLE READ",
    "READ COMMITTED",
    "READ UNCOMMITTED",
    "AUTOCOMMIT",
]


class DBConnectionSchema(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    isolation_level: IsolationLevelType = "READ COMMITTED"
    expire_on_commit: bool = False
    rollback: bool = False
    conn_pool_size: int = 10
    conn_pool_recycle: int = 3600


class RedisConnectionSchema(BaseModel):
    host: str
    port: int
    db: int = 0
    password: str | None = None
    decode_responses: bool = True
    socket_timeout: float | None = None
    max_connections: int = 10
