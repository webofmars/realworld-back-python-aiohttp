import typing as t

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from conduit.config import db_url
from conduit.db.tables import METADATA


@pytest.fixture
async def db_engine() -> t.AsyncIterator[AsyncEngine]:
    engine = create_async_engine(url=db_url(), echo=True)
    async with engine.begin() as connection:
        await connection.run_sync(METADATA.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(METADATA.drop_all)
    engine.sync_engine.dispose()
