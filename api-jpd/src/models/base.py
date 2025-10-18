from datetime import datetime
from typing import ClassVar

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.sqltypes import REAL, TIMESTAMP, Integer, String

from models.mixins import DictMixin

meta = MetaData()


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
    type_annotation_map: ClassVar = {
        int: Integer,
        float: REAL,
        datetime: TIMESTAMP(timezone=False),
        str: String(256),
    }


class BaseDBModel(DictMixin, Base):
    __abstract__ = True
