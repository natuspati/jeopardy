from datetime import datetime

from sqlalchemy import TIMESTAMP, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModel


class UserModel(BaseDBModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    password: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    categories: Mapped[list["CategoryModel"]] = relationship(back_populates="owner")
    lobbies: Mapped[list["LobbyModel"]] = relationship(back_populates="host")
