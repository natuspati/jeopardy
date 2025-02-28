from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModelID


class UserModel(BaseDBModelID):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categories: Mapped[list["CategoryModel"]] = relationship(
        back_populates="owner",
    )
