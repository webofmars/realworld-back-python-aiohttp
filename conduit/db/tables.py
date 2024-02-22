__all__ = [
    "FOLLOWER",
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


FOLLOWER = sa.Table(
    "follower",
    METADATA,
    sa.Column("follower_id", sa.BigInteger, sa.ForeignKey(USER.c.id), nullable=False),
    sa.Column("followed_id", sa.BigInteger, sa.ForeignKey(USER.c.id), nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False),
    sa.PrimaryKeyConstraint("follower_id", "followed_id"),
)
