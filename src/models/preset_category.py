from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModel


class PresetCategoryModel(BaseDBModel):
    __tablename__ = "preset_category"

    preset_id: Mapped[int] = mapped_column(
        ForeignKey("preset.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    preset: Mapped["PresetModel"] = relationship(back_populates="category_associations")
    category: Mapped["CategoryModel"] = relationship(
        back_populates="preset_associations",
    )
