__all__ = [
    "GetProfileInput",
    "GetProfileResult",
    "GetProfileUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput

LOG = logging.getLogger(__name__)


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
        async with self._unit_of_work.begin() as uow:
            user = await uow.users.get_by_username(input.username)
        if user is None:
            LOG.info("user not found", extra={"input": input})
            return GetProfileResult(None, False)
        if input.user_id is not None:
            LOG.info("user is authenticated, check if profile is followed", extra={"input": input})
            async with self._unit_of_work.begin() as uow:
                is_followed = await uow.followers.is_followed(user.id, by=input.user_id)
        else:
            LOG.info("user is not authenticated, profile is not followed", extra={"input": input})
            is_followed = False
        return GetProfileResult(user, is_followed)
