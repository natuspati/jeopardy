from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModelID


class CategoryModel(BaseDBModelID):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        index=True,
        nullable=False,
    )

    owner: Mapped["UserModel"] = relationship(
        back_populates="categories",
    )
    prompts: Mapped[list["PromptModel"]] = relationship(
        back_populates="category",
        cascade="all, delete, delete-orphan",
    )
