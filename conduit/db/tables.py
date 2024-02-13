__all__ = [
    "METADATA",
    "USER",
]

import sqlalchemy as sa

METADATA = sa.MetaData()


USER = sa.Table(
    "user",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("username", sa.Text, nullable=False, unique=True),
    sa.Column("email", sa.Text, nullable=False, unique=True),
    sa.Column("password_hash", sa.Text, nullable=False),
    sa.Column("bio", sa.Text, nullable=False),
    sa.Column("image_url", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False),
    sa.Column("updated_at", sa.DateTime, nullable=True),
)
