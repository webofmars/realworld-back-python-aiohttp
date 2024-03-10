__all__ = [
    "UnfollowInput",
    "UnfollowResult",
    "UnfollowUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = structlog.get_logger(__name__)


@dataclass(frozen=True)
class UnfollowInput(WithAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UnfollowResult:
    user: User | None


class UnfollowUseCase(UseCase[UnfollowInput, UnfollowResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: UnfollowInput, /) -> UnfollowResult:
        """Unfollow an user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        log = LOG.bind(input=input)
        user_id = input.ensure_authenticated()
        async with self._unit_of_work.begin() as uow:
            unfollowed_user = await uow.users.get_by_username(input.username)
        if unfollowed_user is None:
            log.info("could not unfollow user, user not found")
            return UnfollowResult(None)
        async with self._unit_of_work.begin() as uow:
            await uow.followers.unfollow(follower_id=user_id, followed_id=unfollowed_user.id)
        log.info("user is unfollowed", unfollowed_user_id=unfollowed_user.id)
        return UnfollowResult(unfollowed_user)
