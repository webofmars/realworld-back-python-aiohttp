import typing as t

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from conduit.config import db_url
from conduit.core.entities.user import CreateUserInput, Email, PasswordHash, User, Username
from conduit.db.tables import METADATA
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
