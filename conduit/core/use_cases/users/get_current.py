__all__ = [
    "GetCurrentUserInput",
    "GetCurrentUserResult",
    "GetCurrentUserUseCase",
]

import logging
from dataclasses import dataclass, replace

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import AuthToken, User, UserId
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
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: GetCurrentUserInput, /) -> GetCurrentUserResult:
        """Get current user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        async with self._unit_of_work.begin() as uow:
            user = await uow.users.get_by_id(user_id)
        if user is None:
            LOG.warning("authenticated user not found", extra={"user_id": input.user_id})
            raise UserIsNotAuthenticatedError()
        return GetCurrentUserResult(user, input.token)
