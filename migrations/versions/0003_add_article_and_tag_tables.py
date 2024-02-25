"""add article and tag tables.

Revision ID: 0003
Revises: 0002
Create Date: 2024-02-25 12:19:28.681078

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tag",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("tag", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tag"),
    )
    op.create_table(
        "article",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_article_author_id"), "article", ["author_id"], unique=False)
    op.create_table(
        "article_tag",
        sa.Column("article_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["article_id"],
            ["article.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )
    op.create_index(op.f("ix_article_tag_tag_id"), "article_tag", ["tag_id"], unique=False)
    op.create_table(
        "favorite_article",
        sa.Column("article_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["article_id"],
            ["article.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("article_id", "user_id"),
    )
    op.create_index(op.f("ix_favorite_article_user_id"), "favorite_article", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_favorite_article_user_id"), table_name="favorite_article")
    op.drop_table("favorite_article")
    op.drop_index(op.f("ix_article_tag_tag_id"), table_name="article_tag")
    op.drop_table("article_tag")
    op.drop_index(op.f("ix_article_author_id"), table_name="article")
    op.drop_table("article")
    op.drop_table("tag")
