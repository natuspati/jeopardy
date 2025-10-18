from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModel


class CategoryModel(BaseDBModel):
    __tablename__ = "prompt_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    owner: Mapped["UserModel"] = relationship(back_populates="categories")

    lobby_categories: Mapped[list["LobbyCategoryModel"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    lobbies: Mapped[list["LobbyModel"]] = relationship(
        secondary="lobby_category",
        back_populates="categories",
        viewonly=True,
    )

    prompts: Mapped[list["PromptModel"]] = relationship(back_populates="category")
