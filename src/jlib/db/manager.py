import contextlib
import logging
from collections.abc import AsyncIterator

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from jlib.errors.database import DBSessionManagerClosedError
from jlib.types.database import IsolationLevelType

_logger = logging.getLogger(__name__)


class DBManager:
    def __init__(
        self,
        db_url: str | URL,
        db_echo: bool = False,
        db_echo_pool: bool = False,
        db_isolation_level: IsolationLevelType = "READ COMMITTED",
        db_expire_on_commit: bool = False,
        rollback: bool = False,
    ):
        self.db_url = db_url
        self._force_fk_enabling = str(db_url).startswith("sqlite")
        self._engine = create_async_engine(
            url=db_url,
            echo=db_echo,
            echo_pool=db_echo_pool,
            isolation_level=db_isolation_level,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=db_expire_on_commit,
        )
        self._rollback = rollback

    async def close(self) -> None:
        """
        Close session to database.

        :return:
        """
        if self._engine is None:
            raise DBSessionManagerClosedError()
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
            raise DBSessionManagerClosedError()

        async with self._engine.begin() as connection:
            try:
                await self._ensure_fks(connection)
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
        if self._sessionmaker is None:
            raise DBSessionManagerClosedError()

        async with self._sessionmaker() as session, session.begin():
            try:
                await self._ensure_fks(session)
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

    async def _ensure_fks(self, connectable: AsyncConnection | AsyncSession) -> None:
        """Ensure foreign keys are enabled."""
        if self._force_fk_enabling:
            await connectable.execute(text("PRAGMA foreign_keys=ON;"))
