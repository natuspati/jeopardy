import contextlib
import logging
from collections.abc import AsyncIterator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from errors.storage import DBError
from schemas.storage import DBConnectionSchema

_logger = logging.getLogger(__name__)


class DBManager:
    def __init__(
        self,
        *,
        db_url: str | URL,
        conn_config: DBConnectionSchema,
    ):
        self.db_url = db_url
        self._engine = create_async_engine(
            url=db_url,
            echo=conn_config.echo,
            echo_pool=conn_config.echo_pool,
            isolation_level=conn_config.isolation_level,
            pool_size=conn_config.conn_pool_size,
            pool_recycle=conn_config.conn_pool_recycle,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=conn_config.expire_on_commit,
        )
        self._rollback = conn_config.rollback

    async def close(self) -> None:
        """
        Close session to database.

        :return:
        """
        if self._engine is None:
            raise DBError()
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Connect to database.

        :yield: database connection
        """
        if self._engine is None:
            raise DBError()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as error:
                _logger.exception(
                    "An exception was raised during connection",
                    exc_info=error,
                )
                await connection.rollback()
                raise error
            else:
                if self._rollback:
                    await connection.rollback()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Create session to database.

        If `_rollback` is True, all transactions are rolled back. By default,
        transactions are rolled back if Exception occurs.

        :yield: database session
        """
        if self._engine is None:
            raise DBError()

        async with self._sessionmaker() as session, session.begin():
            try:
                yield session
            except Exception as error:
                _logger.exception(
                    "An exception was raised during session",
                    exc_info=error,
                )
                await session.rollback()
                raise error
            else:
                if self._rollback:
                    await session.rollback()
