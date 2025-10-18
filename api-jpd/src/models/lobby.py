from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModel


class LobbyModel(BaseDBModel):
    __tablename__ = "lobby"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    host: Mapped["UserModel"] = relationship(back_populates="lobbies")

    lobby_categories: Mapped[list["LobbyCategoryModel"]] = relationship(
        back_populates="lobby",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    categories: Mapped[list["CategoryModel"]] = relationship(
        secondary="lobby_category",
        back_populates="lobbies",
        viewonly=True,
    )
