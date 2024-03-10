__all__ = [
    "WithAuthentication",
    "WithAuthenticationInput",
    "WithOptionalAuthenticationInput",
]

import typing as t
from dataclasses import dataclass

import structlog

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, AuthTokenGenerator, UserId
from conduit.core.use_cases import UseCase

LOG = structlog.get_logger(__name__)


T = t.TypeVar("T", bound="Input")
R = t.TypeVar("R")


class Input(t.Protocol):
    @property
    def token(self) -> AuthToken | None:
        raise NotImplementedError()

    def with_user_id(self, id: UserId) -> t.Self:
        raise NotImplementedError()


@dataclass(frozen=True)
class WithAuthenticationInput:
    token: AuthToken
    user_id: UserId | None

    def ensure_authenticated(self) -> UserId:
        if self.user_id is None:
            raise UserIsNotAuthenticatedError()
        return self.user_id


@dataclass(frozen=True)
class WithOptionalAuthenticationInput:
    token: AuthToken | None
    user_id: UserId | None


class WithAuthentication(UseCase[T, R]):
    def __init__(
        self,
        auth_token_generator: AuthTokenGenerator,
        use_case: UseCase[T, R],
    ) -> None:
        self._auth_token_generator = auth_token_generator
        self._use_case = use_case

    async def execute(self, input: T, /) -> R:
        user_id = await self._auth_token_generator.get_user_id(input.token) if input.token is not None else None
        if user_id is not None:
            input = input.with_user_id(user_id)
            LOG.info("user authenticated", user_id=user_id)
        else:
            LOG.info("auth token is not provided or invalid")
        return await self._use_case.execute(input)
