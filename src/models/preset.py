from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModelID


class PresetModel(BaseDBModelID):
    __tablename__ = "preset"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        index=True,
        nullable=False,
    )

    owner: Mapped["UserModel"] = relationship(
        back_populates="presets",
    )
    categories: Mapped[list["CategoryModel"]] = relationship(
        secondary="preset_category",
        back_populates="presets",
        viewonly=True,
    )
    category_associations: Mapped[list["PresetCategoryModel"]] = relationship(
        back_populates="preset",
        cascade="all, delete, delete-orphan",
    )
