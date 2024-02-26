__all__ = [
    "PostgresqlFollowerRepository",
]

import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from conduit.core.entities.user import FollowerRepository, UserId
from conduit.db import tables


class PostgresqlFollowerRepository(FollowerRepository):
    def __init__(
        self,
        connection: AsyncConnection,
        now: t.Callable[[], dt.datetime] = dt.datetime.utcnow,
    ) -> None:
        self._connection = connection
        self._now = now

    async def follow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        stmt = (
            insert(tables.FOLLOWER)
            .values(follower_id=follower_id, followed_id=followed_id, created_at=self._now())
            .on_conflict_do_nothing()
        )
        await self._connection.execute(stmt)

    async def unfollow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        stmt = sa.delete(tables.FOLLOWER).where(
            tables.FOLLOWER.c.follower_id == follower_id, tables.FOLLOWER.c.followed_id == followed_id
        )
        await self._connection.execute(stmt)

    async def is_followed(self, id: UserId, *, by: UserId) -> bool:
        stmt = sa.select(tables.FOLLOWER.c.followed_id).where(
            tables.FOLLOWER.c.follower_id == by, tables.FOLLOWER.c.followed_id == id
        )
        result = await self._connection.execute(stmt)
        followed_id = result.scalar_one_or_none()
        return followed_id is not None

    async def are_followed(self, ids: t.Collection[UserId], by: UserId) -> dict[UserId, bool]:
        if not ids:
            return {}
        stmt = sa.select(tables.FOLLOWER.c.followed_id).where(
            tables.FOLLOWER.c.follower_id == by, tables.FOLLOWER.c.followed_id.in_(ids)
        )
        result = await self._connection.execute(stmt)
        followed_ids = set(result.scalars())
        return {id: id in followed_ids for id in ids}
