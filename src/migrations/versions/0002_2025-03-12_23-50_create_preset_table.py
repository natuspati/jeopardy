"""Create preset table.

Revision ID: 0002
Revises: 0001
Create Date: 2025-03-12 23:50:43.906303

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "preset",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_preset_id"), "preset", ["id"], unique=False)
    op.create_index(op.f("ix_preset_owner_id"), "preset", ["owner_id"], unique=False)

    op.create_table(
        "preset_category",
        sa.Column("preset_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["preset_id"], ["preset.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("preset_id", "category_id"),
    )
    op.create_index(
        op.f("ix_preset_category_category_id"),
        "preset_category",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_preset_category_preset_id"),
        "preset_category",
        ["preset_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_preset_category_preset_id"), table_name="preset_category")
    op.drop_index(op.f("ix_preset_category_category_id"), table_name="preset_category")
    op.drop_table("preset_category")
    op.drop_index(op.f("ix_preset_owner_id"), table_name="preset")
    op.drop_index(op.f("ix_preset_id"), table_name="preset")
    op.drop_table("preset")
