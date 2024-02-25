import datetime as dt
import typing as t
from secrets import token_urlsafe

import sqlalchemy as sa
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncConnection

from conduit.core.entities.article import (
    Article,
    ArticleFilter,
    ArticleId,
    ArticleRepository,
    ArticleSlug,
    CreateArticleInput,
    UpdateArticleInput,
)
from conduit.core.entities.common import NotSet
from conduit.core.entities.user import UserId
from conduit.db import tables


class PostgresqlArticleRepository(ArticleRepository):
    def __init__(self, connection: AsyncConnection, now: t.Callable[[], dt.datetime] = dt.datetime.utcnow) -> None:
        self._connection = connection
        self._now = now

    async def create(self, input: CreateArticleInput) -> Article:
        stmt = (
            sa.insert(tables.ARTICLE)
            .values(
                author_id=input.author_id,
                slug=self._slugify(input.title),
                title=input.title,
                description=input.description,
                body=input.body,
                created_at=self._now(),
            )
            .returning(tables.ARTICLE)
        )
        result = await self._connection.execute(stmt)
        return self._decode_article(result.one())

    async def get_many(self, filter: ArticleFilter, *, limit: int, offset: int) -> list[Article]:
        stmt = sa.select(tables.ARTICLE)
        stmt = self._apply_filter(stmt, filter)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._connection.execute(stmt)
        rows = result.all()
        return [self._decode_article(row) for row in rows]

    async def count(self, filter: ArticleFilter) -> int:
        stmt = sa.select(sa.func.count(tables.ARTICLE.c.id))
        stmt = self._apply_filter(stmt, filter)
        result = await self._connection.execute(stmt)
        return result.scalar_one()

    async def get_by_slug(self, slug: ArticleSlug) -> Article | None:
        stmt = sa.select(tables.ARTICLE).where(tables.ARTICLE.c.slug == slug)
        result = await self._connection.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        return self._decode_article(row)

    async def update(self, id: ArticleId, input: UpdateArticleInput) -> Article | None:
        stmt = (
            sa.update(tables.ARTICLE)
            .where(tables.ARTICLE.c.id == id)
            .values(updated_at=self._now())
            .returning(tables.ARTICLE)
        )
        if input.title is not NotSet.NOT_SET:
            stmt = stmt.values(title=input.title, slug=self._slugify(input.title))
        if input.description is not NotSet.NOT_SET:
            stmt = stmt.values(description=input.description)
        if input.body is not NotSet.NOT_SET:
            stmt = stmt.values(body=input.body)
        result = await self._connection.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        return self._decode_article(row)

    async def delete(self, id: ArticleId) -> ArticleId | None:
        stmt = sa.delete(tables.ARTICLE).where(tables.ARTICLE.c.id == id).returning(tables.ARTICLE.c.id)
        result = await self._connection.execute(stmt)
        scalar = result.scalar_one_or_none()
        if scalar is None:
            return None
        return ArticleId(scalar)

    def _slugify(self, title: str) -> ArticleSlug:
        slug = slugify(title, max_length=32, lowercase=False)
        token = token_urlsafe(8)
        return ArticleSlug(f"{slug}-{token}")

    def _decode_article(self, db_row: t.Any) -> Article:
        return Article(
            id=ArticleId(db_row.id),
            author_id=UserId(db_row.author_id),
            slug=ArticleSlug(db_row.slug),
            title=db_row.title,
            description=db_row.description,
            body=db_row.body,
            created_at=db_row.created_at,
            updated_at=db_row.updated_at,
        )

    def _apply_filter(self, stmt: sa.Select[t.Any], filter: ArticleFilter) -> sa.Select[t.Any]:
        if filter.tag is not None:
            stmt = (
                stmt.join_from(
                    tables.ARTICLE, tables.ARTICLE_TAG, onclause=tables.ARTICLE.c.id == tables.ARTICLE_TAG.c.article_id
                )
                .join_from(tables.ARTICLE_TAG, tables.TAG, onclause=tables.ARTICLE_TAG.c.tag_id == tables.TAG.c.id)
                .where(tables.TAG.c.tag == filter.tag)
            )
        if filter.author is not None:
            stmt = stmt.join_from(
                tables.ARTICLE, tables.USER, onclause=tables.ARTICLE.c.author_id == tables.USER.c.id
            ).where(tables.USER.c.username == filter.author)
        if filter.favorite_of is not None:
            stmt = (
                stmt.join_from(
                    tables.ARTICLE,
                    tables.FAVORITE_ARTICLE,
                    onclause=tables.ARTICLE.c.id == tables.FAVORITE_ARTICLE.c.article_id,
                )
                .join_from(
                    tables.FAVORITE_ARTICLE,
                    tables.USER,
                    onclause=tables.FAVORITE_ARTICLE.c.user_id == tables.USER.c.id,
                )
                .where(tables.USER.c.username == filter.favorite_of)
            )
        if filter.feed_of is not None:
            stmt = stmt.join_from(
                tables.ARTICLE,
                tables.FOLLOWER,
                onclause=tables.ARTICLE.c.author_id == tables.FOLLOWER.c.followed_id,
            ).where(tables.FOLLOWER.c.follower_id == filter.feed_of)
        return stmt
