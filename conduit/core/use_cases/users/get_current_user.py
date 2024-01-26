__all__ = [
    "GetCurrentUserInput",
    "GetCurrentUserResult",
    "GetCurrentUserUseCase",
]

import logging
from dataclasses import dataclass, replace

from conduit.core.entities.errors import UserDoesNotExistError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, UserId, UserRepository
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetCurrentUserInput(WithAuthenticationInput):
    def with_user_id(self, id: UserId) -> "GetCurrentUserInput":
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetCurrentUserResult:
    user: User
    token: AuthToken


class GetCurrentUserUseCase(UseCase[GetCurrentUserInput, GetCurrentUserResult]):
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, input: GetCurrentUserInput, /) -> GetCurrentUserResult:
        """Get current user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            UserDoesNotExistError: If user does not exist.
        """
        if input.user_id is None:
            LOG.info("user is not authenticated")
            raise UserIsNotAuthenticatedError()
        user = await self._user_repository.get_by_id(input.user_id)
        if user is None:
            LOG.warning("authenticated user not found", extra={"user_id": input.user_id})
            raise UserDoesNotExistError()
        return GetCurrentUserResult(user, input.token)
