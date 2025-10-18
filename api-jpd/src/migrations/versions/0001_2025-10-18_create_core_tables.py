"""
Create core tables.

Revision ID: 0001
Revises:
Create Date: 2025-10-18 19:01:16.946122

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=16), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)

    op.create_table(
        "lobby",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["host_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "prompt_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lobby_category",
        sa.Column("lobby_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["prompt_category.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lobby_id"], ["lobby.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("lobby_id", "category_id"),
    )

    op.create_table(
        "prompt",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=256), nullable=False),
        sa.Column(
            "question_type",
            sa.Enum("TEXT", "IMAGE", "VIDEO", name="prompt_type_enum"),
            nullable=False,
        ),
        sa.Column("answer", sa.String(length=256), nullable=False),
        sa.Column(
            "answer_type",
            sa.Enum("TEXT", "IMAGE", "VIDEO", name="prompt_type_enum"),
            nullable=False,
        ),
        sa.Column("order", sa.SmallInteger(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["prompt_category.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", "order", name="uq_prompt_category_order"),
    )


def downgrade() -> None:
    op.drop_table("prompt")
    op.drop_table("lobby_category")
    op.drop_table("prompt_category")
    op.drop_table("lobby")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")
