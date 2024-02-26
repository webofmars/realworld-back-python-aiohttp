__all__ = [
    "PostgresqlCommentRepository",
]

import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from conduit.core.entities.article import ArticleId
from conduit.core.entities.comment import Comment, CommentFilter, CommentId, CommentRepository, CreateCommentInput
from conduit.core.entities.user import UserId
from conduit.db import tables


class PostgresqlCommentRepository(CommentRepository):
    def __init__(self, connection: AsyncConnection, now: t.Callable[[], dt.datetime] = dt.datetime.utcnow) -> None:
        self._connection = connection
        self._now = now

    async def create(self, input: CreateCommentInput) -> Comment:
        stmt = (
            sa.insert(tables.COMMENT)
            .values(author_id=input.author_id, article_id=input.article_id, body=input.body, created_at=self._now())
            .returning(tables.COMMENT)
        )
        result = await self._connection.execute(stmt)
        row = result.one()
        return self._decode_comment(row)

    async def get_many(self, filter: CommentFilter) -> list[Comment]:
        stmt = sa.select(tables.COMMENT)
        if filter.article_id is not None:
            stmt = stmt.where(tables.COMMENT.c.article_id == filter.article_id)
        stmt = stmt.order_by(tables.COMMENT.c.id)
        result = await self._connection.execute(stmt)
        rows = result.all()
        return [self._decode_comment(row) for row in rows]

    async def get_by_id(self, id: CommentId) -> Comment | None:
        stmt = sa.select(tables.COMMENT).where(tables.COMMENT.c.id == id)
        result = await self._connection.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        return self._decode_comment(row)

    async def delete(self, id: CommentId) -> CommentId | None:
        stmt = sa.delete(tables.COMMENT).where(tables.COMMENT.c.id == id).returning(tables.COMMENT.c.id)
        result = await self._connection.execute(stmt)
        comment_id = result.scalar_one_or_none()
        if comment_id is None:
            return None
        assert isinstance(comment_id, int)
        return CommentId(comment_id)

    def _decode_comment(self, db_row: t.Any) -> Comment:
        return Comment(
            id=CommentId(db_row.id),
            author_id=UserId(db_row.author_id),
            article_id=ArticleId(db_row.article_id),
            body=db_row.body,
            created_at=db_row.created_at,
            updated_at=db_row.updated_at,
        )
