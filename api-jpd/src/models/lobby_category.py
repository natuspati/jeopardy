from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModel


class LobbyCategoryModel(BaseDBModel):
    __tablename__ = "lobby_category"

    lobby_id: Mapped[int] = mapped_column(
        ForeignKey("lobby.id", ondelete="CASCADE"),
        primary_key=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("prompt_category.id", ondelete="CASCADE"),
        primary_key=True,
    )

    lobby: Mapped["LobbyModel"] = relationship(back_populates="lobby_categories")
    category: Mapped["CategoryModel"] = relationship(back_populates="lobby_categories")
