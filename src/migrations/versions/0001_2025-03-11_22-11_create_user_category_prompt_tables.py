"""Create user, category, prompt tables

Revision ID: 0001
Revises:
Create Date: 2025-03-11 22:11:48.231163

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)

    op.create_table(
        "category",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_category_id"), "category", ["id"], unique=False)
    op.create_index(op.f("ix_category_name"), "category", ["name"], unique=True)
    op.create_index(
        op.f("ix_category_owner_id"),
        "category",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "prompt",
        sa.Column("question", sa.String(length=1023), nullable=False),
        sa.Column("question_type", sa.SmallInteger(), nullable=False),
        sa.Column("answer", sa.String(length=1023), nullable=False),
        sa.Column("answer_type", sa.SmallInteger(), nullable=False),
        sa.Column("default_priority", sa.SmallInteger(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "default_priority",
            "category_id",
            name="uq_prompt_priority_in_category",
        ),
    )
    op.create_index(op.f("ix_prompt_id"), "prompt", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_prompt_id"), table_name="prompt")
    op.drop_table("prompt")

    op.drop_index(op.f("ix_category_owner_id"), table_name="category")
    op.drop_index(op.f("ix_category_name"), table_name="category")
    op.drop_index(op.f("ix_category_id"), table_name="category")
    op.drop_table("category")

    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")
