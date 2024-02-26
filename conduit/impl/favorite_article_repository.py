__all__ = [
    "PostgresqlFavoriteArticleRepository",
]
import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from conduit.core.entities.article import ArticleId, FavoriteRepository
from conduit.core.entities.user import UserId
from conduit.db import tables


class PostgresqlFavoriteArticleRepository(FavoriteRepository):
    def __init__(self, connection: AsyncConnection, now: t.Callable[[], dt.datetime] = dt.datetime.utcnow) -> None:
        self._connection = connection
        self._now = now

    async def add(self, user_id: UserId, article_id: ArticleId) -> int:
        insert_stmt = (
            insert(tables.FAVORITE_ARTICLE)
            .on_conflict_do_nothing()
            .values(user_id=user_id, article_id=article_id, created_at=self._now())
        )
        await self._connection.execute(insert_stmt)
        count_stmt = self._count_stmt(article_id)
        result = await self._connection.execute(count_stmt)
        count = result.scalar_one()
        assert isinstance(count, int)
        return count

    async def remove(self, user_id: UserId, article_id: ArticleId) -> int:
        delete_stmt = (
            sa.delete(tables.FAVORITE_ARTICLE)
            .where(tables.FAVORITE_ARTICLE.c.user_id == user_id)
            .where(tables.FAVORITE_ARTICLE.c.article_id == article_id)
        )
        await self._connection.execute(delete_stmt)
        count_stmt = self._count_stmt(article_id)
        result = await self._connection.execute(count_stmt)
        count = result.scalar_one()
        assert isinstance(count, int)
        return count

    async def is_favorite(self, article_id: ArticleId, of: UserId) -> bool:
        stmt = (
            sa.select(tables.FAVORITE_ARTICLE.c.article_id)
            .where(tables.FAVORITE_ARTICLE.c.user_id == of)
            .where(tables.FAVORITE_ARTICLE.c.article_id == article_id)
        )
        result = await self._connection.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def are_favorite(self, article_ids: t.Collection[ArticleId], of: UserId) -> dict[ArticleId, bool]:
        if not article_ids:
            return {}
        stmt = (
            sa.select(tables.FAVORITE_ARTICLE.c.article_id)
            .where(tables.FAVORITE_ARTICLE.c.user_id == of)
            .where(tables.FAVORITE_ARTICLE.c.article_id.in_(article_ids))
        )
        result = await self._connection.execute(stmt)
        return {article_id: True for article_id in result.scalars()}

    async def count(self, article_id: ArticleId) -> int:
        stmt = self._count_stmt(article_id)
        result = await self._connection.execute(stmt)
        count = result.scalar_one()
        assert isinstance(count, int)
        return count

    async def count_many(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, int]:
        if not article_ids:
            return {}
        stmt = (
            sa.select(
                tables.FAVORITE_ARTICLE.c.article_id,
                sa.func.count(tables.FAVORITE_ARTICLE.c.user_id).label("count_"),
            )
            .where(tables.FAVORITE_ARTICLE.c.article_id.in_(article_ids))
            .group_by(tables.FAVORITE_ARTICLE.c.article_id)
        )
        result = await self._connection.execute(stmt)
        return {row.article_id: row.count_ for row in result.all()}

    def _count_stmt(self, article_id: ArticleId) -> sa.Select[t.Any]:
        return sa.select(sa.func.count(tables.FAVORITE_ARTICLE.c.user_id)).where(
            tables.FAVORITE_ARTICLE.c.article_id == article_id
        )
