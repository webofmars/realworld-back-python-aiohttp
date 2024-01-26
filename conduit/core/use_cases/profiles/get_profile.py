__all__ = [
    "GetProfileInput",
    "GetProfileResult",
    "GetProfileUseCase",
]

import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.profile import Profile, ProfileRepository
from conduit.core.entities.user import UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput


@dataclass(frozen=True)
class GetProfileInput(WithOptionalAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetProfileResult:
    profile: Profile | None


class GetProfileUseCase(UseCase[GetProfileInput, GetProfileResult]):
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def execute(self, input: GetProfileInput, /) -> GetProfileResult:
        profile = await self._profile_repository.get(input.username, is_following_by=input.user_id)
        return GetProfileResult(profile)
