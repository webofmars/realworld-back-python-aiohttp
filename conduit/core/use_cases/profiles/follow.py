__all__ = [
    "FollowInput",
    "FollowResult",
    "FollowUseCase",
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
class FollowInput(WithAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class FollowResult:
    user: User | None


class FollowUseCase(UseCase[FollowInput, FollowResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: FollowInput, /) -> FollowResult:
        """Follow an user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        log = LOG.bind(input=input)
        user_id = input.ensure_authenticated()
        async with self._unit_of_work.begin() as uow:
            followed_user = await uow.users.get_by_username(input.username)
        if followed_user is None:
            log.info("could not follow user, user not found")
            return FollowResult(None)
        async with self._unit_of_work.begin() as uow:
            await uow.followers.follow(follower_id=user_id, followed_id=followed_user.id)
        log.info("user is followed", followed_user_id=followed_user.id)
        return FollowResult(followed_user)
