from datetime import datetime
from typing import Any

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

    def to_dict(self) -> dict[str, Any]:
        model_as_dict = self.__dict__
        model_as_dict.pop("_sa_instance_state")
        return model_as_dict


class BaseDBModelID(BaseDBModel, IDDBMixin):
    __abstract__ = True
