__all__ = [
    "FakeUseCase",
]

import typing as t

import pytest
from aiohttp.test_utils import TestClient
from pytest_aiohttp.plugin import AiohttpClient

from conduit.container import create_app
from conduit.core.use_cases import UseCase

T = t.TypeVar("T", contravariant=True)
R = t.TypeVar("R", covariant=True)


class FakeUseCase(UseCase[T, R]):
    def __init__(self) -> None:
        self.input: T | None = None
        self.result: R | None = None

    async def execute(self, input: T, /) -> R:
        self.input = input
        assert self.result is not None
        return self.result


@pytest.fixture
async def client(aiohttp_client: AiohttpClient) -> TestClient:
    app = create_app()
    client = await aiohttp_client(app)
    assert isinstance(client, TestClient)
    return client
