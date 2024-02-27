import typing as t
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.impl.article_repository import PostgresqlArticleRepository
from conduit.impl.comment_repository import PostgresqlCommentRepository
from conduit.impl.favorite_article_repository import PostgresqlFavoriteArticleRepository
from conduit.impl.follower_repository import PostgresqlFollowerRepository
from conduit.impl.tag_repository import PostgresqlTagRepository
from conduit.impl.user_repository import PostgresqlUserRepository


@dataclass(frozen=True)
class PostgresqlUnitOfWorkContext:
    users: PostgresqlUserRepository
    followers: PostgresqlFollowerRepository
    articles: PostgresqlArticleRepository
    tags: PostgresqlTagRepository
    favorites: PostgresqlFavoriteArticleRepository
    comments: PostgresqlCommentRepository


class PostgresqlUnitOfWork(UnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @asynccontextmanager
    async def begin(self) -> t.AsyncIterator[PostgresqlUnitOfWorkContext]:
        async with self._engine.begin() as connection:
            yield PostgresqlUnitOfWorkContext(
                users=PostgresqlUserRepository(connection),
                followers=PostgresqlFollowerRepository(connection),
                articles=PostgresqlArticleRepository(connection),
                tags=PostgresqlTagRepository(connection),
                favorites=PostgresqlFavoriteArticleRepository(connection),
                comments=PostgresqlCommentRepository(connection),
            )
