import typing as t

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from conduit.config import db_url
from conduit.core.entities.article import Article, CreateArticleInput
from conduit.core.entities.user import CreateUserInput, Email, PasswordHash, User, Username
from conduit.db.tables import METADATA
from conduit.impl.article_repository import PostgresqlArticleRepository
from conduit.impl.user_repository import PostgresqlUserRepository


@pytest.fixture
async def db_engine() -> t.AsyncIterator[AsyncEngine]:
    engine = create_async_engine(url=db_url(), echo=True)
    async with engine.begin() as connection:
        await connection.run_sync(METADATA.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(METADATA.drop_all)
    await engine.dispose()


@pytest.fixture
async def existing_users(db_engine: AsyncEngine) -> tuple[User, User]:
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        u1 = await repo.create(CreateUserInput(Username("test-1"), Email("test-1@test.test"), PasswordHash("test-1")))
        u2 = await repo.create(CreateUserInput(Username("test-2"), Email("test-2@test.test"), PasswordHash("test-2")))
    return u1, u2


@pytest.fixture
async def existing_articles(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> list[Article]:
    user_1, user_2 = existing_users
    create_inputs = [
        CreateArticleInput(user_1.id, "title-1", "description-1", "body-1"),
        CreateArticleInput(user_1.id, "title-2", "description-2", "body-2"),
        CreateArticleInput(user_2.id, "title-3", "description-3", "body-3"),
        CreateArticleInput(user_2.id, "title-4", "description-4", "body-4"),
    ]
    articles = []
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        for input in create_inputs:
            article = await repo.create(input)
            articles.append(article)
    return articles
