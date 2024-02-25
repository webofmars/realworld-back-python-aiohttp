__all__ = [
    "ARTICLE",
    "ARTICLE_TAG",
    "FAVORITE_ARTICLE",
    "FOLLOWER",
    "METADATA",
    "TAG",
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


ARTICLE = sa.Table(
    "article",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("author_id", sa.BigInteger, sa.ForeignKey(USER.c.id), nullable=False, index=True),
    sa.Column("slug", sa.Text, nullable=False, unique=True),
    sa.Column("title", sa.Text, nullable=False),
    sa.Column("description", sa.Text, nullable=False),
    sa.Column("body", sa.Text, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False),
    sa.Column("updated_at", sa.DateTime, nullable=True),
)


TAG = sa.Table(
    "tag",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("tag", sa.Text, nullable=False, unique=True),
    sa.Column("created_at", sa.DateTime, nullable=False),
)


ARTICLE_TAG = sa.Table(
    "article_tag",
    METADATA,
    sa.Column("article_id", sa.BigInteger, sa.ForeignKey(ARTICLE.c.id), nullable=False),
    sa.Column("tag_id", sa.BigInteger, sa.ForeignKey(TAG.c.id), nullable=False, index=True),
    sa.Column("created_at", sa.DateTime, nullable=False),
    sa.PrimaryKeyConstraint("article_id", "tag_id"),
)


FAVORITE_ARTICLE = sa.Table(
    "favorite_article",
    METADATA,
    sa.Column("article_id", sa.BigInteger, sa.ForeignKey(ARTICLE.c.id), nullable=False),
    sa.Column("user_id", sa.BigInteger, sa.ForeignKey(USER.c.id), nullable=False, index=True),
    sa.Column("created_at", sa.DateTime, nullable=False),
    sa.PrimaryKeyConstraint("article_id", "user_id"),
)
