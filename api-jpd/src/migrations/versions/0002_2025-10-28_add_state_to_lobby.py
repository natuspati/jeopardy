"""
Add state to lobby.

Revision ID: 0002
Revises: 0001
Create Date: 2025-10-28 12:13:59.943936

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    lobby_state_enum = sa.Enum("CREATED", "STARTED", "FINISHED", name="lobby_state_enum")
    lobby_state_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "lobby",
        sa.Column(
            "state",
            sa.Enum("CREATED", "STARTED", "FINISHED", name="lobby_state_enum"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("lobby", "state")

    lobby_state_enum = sa.Enum("CREATED", "STARTED", "FINISHED", name="lobby_state_enum")
    lobby_state_enum.drop(op.get_bind(), checkfirst=True)
