"""add follower table.

Revision ID: 0002
Revises: 0001
Create Date: 2024-02-22 22:49:34.021205

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
        "follower",
        sa.Column("follower_id", sa.BigInteger(), nullable=False),
        sa.Column("followed_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["followed_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["follower_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )


def downgrade() -> None:
    op.drop_table("follower")
