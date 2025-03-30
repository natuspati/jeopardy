import contextlib
import logging
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy import Executable
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.exc import (
    DataError,
    DBAPIError,
    IntegrityError,
    ProgrammingError,
    ResourceClosedError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from jlib.db import DBManager, get_db_manager
from jlib.errors.database import DatabaseDetailError

_logger = logging.getLogger(__name__)

COMMON_DB_ERRORS = (
    ProgrammingError,
    ResourceClosedError,
    IntegrityError,
    DataError,
    DBAPIError,
    OSError,
)


class RelationalDAL:
    def __init__(
        self,
        db_manager: Annotated[DBManager, Depends(get_db_manager)],
    ):
        self._db_manager = db_manager

    async def execute(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ):
        try:
            async with self._db_manager.session() as session:
                session: AsyncSession
                result = await session.execute(query, params=params)
                session.expunge_all()
        except COMMON_DB_ERRORS as error:
            self._handle_error(error, str(error))
        else:
            return result

    async def scalar(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ):
        try:
            async with self._db_manager.session() as session:
                result = await session.scalar(query, params=params)
                session.expunge_all()
        except COMMON_DB_ERRORS as error:
            self._handle_error(error, str(query))
        else:
            return result

    async def scalars(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ):
        try:
            async with self._db_manager.session() as session:
                scalar_result = await session.scalars(query, params=params)
                realized_result = scalar_result.all()
                session.expunge_all()
        except COMMON_DB_ERRORS as error:
            self._handle_error(error, str(query))
        else:
            return realized_result

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        try:
            async with self._db_manager.session() as session:
                yield session
        except COMMON_DB_ERRORS as error:
            self._handle_error(error, str(error))

    @classmethod
    def _handle_error(cls, error: Exception, statement: str) -> None:
        _logger.error(
            "Database error, statement: {0},\ntype: {1},\nmessage: {2}".format(
                statement,
                type(error),
                error,
            ),
        )
        raise DatabaseDetailError(error)
