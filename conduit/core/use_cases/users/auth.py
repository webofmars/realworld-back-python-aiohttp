__all__ = [
    "WithAuthentication",
]
import logging
import typing as t

from conduit.core.entities.user import AuthToken, AuthTokenGenerator, UserId
from conduit.core.use_cases import UseCase

LOG = logging.getLogger(__name__)


T = t.TypeVar("T", bound="Input")
R = t.TypeVar("R")


class Input(t.Protocol):
    @property
    def token(self) -> AuthToken:
        raise NotImplementedError()

    def with_user_id(self, id: UserId) -> t.Self:
        raise NotImplementedError()


class WithAuthentication(UseCase[T, R]):
    def __init__(
        self,
        auth_token_generator: AuthTokenGenerator,
        use_case: UseCase[T, R],
    ) -> None:
        self._auth_token_generator = auth_token_generator
        self._use_case = use_case

    async def execute(self, input: T, /) -> R:
        user_id = await self._auth_token_generator.get_user_id(input.token)
        if user_id is not None:
            input = input.with_user_id(user_id)
            LOG.info("user authenticated", extra={"user_id": user_id})
        else:
            LOG.info("auth token is not valid")
        return await self._use_case.execute(input)
