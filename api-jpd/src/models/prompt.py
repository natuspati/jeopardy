from sqlalchemy import Enum, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.prompt import PromptTypeEnum
from models.base import BaseDBModel


class PromptModel(BaseDBModel):
    __tablename__ = "prompt"
    __table_args__ = (UniqueConstraint("category_id", "order", name="uq_prompt_category_order"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("prompt_category.id", ondelete="CASCADE"))
    question: Mapped[str]
    question_type: Mapped[PromptTypeEnum] = mapped_column(
        Enum(PromptTypeEnum, name="prompt_type_enum"),
    )
    answer: Mapped[str]
    answer_type: Mapped[PromptTypeEnum] = mapped_column(
        Enum(PromptTypeEnum, name="prompt_type_enum"),
    )
    order: Mapped[int] = mapped_column(SmallInteger)
    score: Mapped[int]

    category: Mapped["CategoryModel"] = relationship(back_populates="prompts")
