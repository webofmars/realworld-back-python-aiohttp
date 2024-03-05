__all__ = [
    "PostgresqlTagRepository",
]

import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from conduit.core.entities.article import ArticleId, Tag, TagRepository
from conduit.db import tables


class PostgresqlTagRepository(TagRepository):
    def __init__(self, connection: AsyncConnection, now: t.Callable[[], dt.datetime] = dt.datetime.utcnow) -> None:
        self._connection = connection
        self._now = now

    async def create(self, article_id: ArticleId, tags: t.Collection[Tag]) -> None:
        if not tags:
            return None
        now = self._now()
        stmt = (
            insert(tables.TAG).on_conflict_do_nothing().values([{"created_at": now, "tag": str(tag)} for tag in tags])
        )
        await self._connection.execute(stmt)
        select_tags_stmt = sa.select(tables.TAG.c.id).where(tables.TAG.c.tag.in_(map(str, tags)))
        result = await self._connection.execute(select_tags_stmt)
        tag_ids = result.scalars()
        stmt = (
            insert(tables.ARTICLE_TAG)
            .on_conflict_do_nothing()
            .values([{"article_id": article_id, "tag_id": tag_id, "created_at": now} for tag_id in tag_ids])
        )
        await self._connection.execute(stmt)

    async def get_all(self) -> list[Tag]:
        stmt = sa.select(tables.TAG).order_by(tables.TAG.c.id)
        result = await self._connection.execute(stmt)
        rows = result.all()
        return [Tag(row.tag) for row in rows]

    async def get_for_article(self, article_id: ArticleId) -> list[Tag]:
        stmt = (
            sa.select(tables.TAG)
            .join_from(tables.TAG, tables.ARTICLE_TAG, onclause=tables.TAG.c.id == tables.ARTICLE_TAG.c.tag_id)
            .where(tables.ARTICLE_TAG.c.article_id == article_id)
            .order_by(tables.TAG.c.tag)
        )
        result = await self._connection.execute(stmt)
        rows = result.all()
        return [Tag(row.tag) for row in rows]

    async def get_for_articles(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, list[Tag]]:
        stmt = (
            sa.select(tables.TAG, tables.ARTICLE_TAG.c.article_id)
            .join_from(tables.TAG, tables.ARTICLE_TAG, onclause=tables.TAG.c.id == tables.ARTICLE_TAG.c.tag_id)
            .where(tables.ARTICLE_TAG.c.article_id.in_(article_ids))
            .order_by(tables.TAG.c.tag)
        )
        result = await self._connection.execute(stmt)
        rows = result.all()
        tags: dict[ArticleId, list[Tag]] = {}
        for row in rows:
            tag = Tag(row.tag)
            article_id = ArticleId(row.article_id)
            tags.setdefault(article_id, [])
            tags[article_id].append(tag)
        return tags
