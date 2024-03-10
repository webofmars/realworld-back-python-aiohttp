__all__ = [
    "GetProfileInput",
    "GetProfileResult",
    "GetProfileUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput

LOG = structlog.get_logger(__name__)


@dataclass(frozen=True)
class GetProfileInput(WithOptionalAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetProfileResult:
    user: User | None
    is_followed: bool


class GetProfileUseCase(UseCase[GetProfileInput, GetProfileResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: GetProfileInput, /) -> GetProfileResult:
        log = LOG.bind(input=input)
        async with self._unit_of_work.begin() as uow:
            user = await uow.users.get_by_username(input.username)
        if user is None:
            log.info("user not found")
            return GetProfileResult(None, False)
        if input.user_id is not None:
            log.info("user is authenticated, check if profile is followed")
            async with self._unit_of_work.begin() as uow:
                is_followed = await uow.followers.is_followed(user.id, by=input.user_id)
        else:
            log.info("user is not authenticated, profile is not followed")
            is_followed = False
        return GetProfileResult(user, is_followed)
