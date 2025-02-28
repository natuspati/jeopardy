from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import NVARCHAR, TIMESTAMP, Integer, String

meta = MetaData()


class IDDBMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
    type_annotation_map = {
        int: Integer,
        datetime: TIMESTAMP(timezone=False),
        str: String().with_variant(NVARCHAR, "postgresql"),
    }


class BaseDBModel(Base):
    __abstract__ = True


class BaseDBModelID(BaseDBModel, IDDBMixin):
    __abstract__ = True
