from sqlalchemy import ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseDBModelID


class PromptModel(BaseDBModelID):
    __tablename__ = "prompt"
    __table_args__ = (
        UniqueConstraint(
            "default_priority",
            "category_id",
            name="uq_prompt_priority_in_category",
        ),
    )

    question: Mapped[str] = mapped_column(
        String(1023),
        nullable=False,
    )
    question_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    answer: Mapped[str] = mapped_column(
        String(1023),
        nullable=False,
    )
    answer_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    default_priority: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped["CategoryModel"] = relationship(back_populates="prompts")
