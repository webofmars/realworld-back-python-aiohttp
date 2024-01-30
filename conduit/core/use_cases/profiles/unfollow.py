__all__ = [
    "UnfollowInput",
    "UnfollowResult",
    "UnfollowUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.profile import Profile, ProfileRepository, UpdateProfileInput
from conduit.core.entities.user import UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UnfollowInput(WithAuthenticationInput):
    username: Username

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UnfollowResult:
    profile: Profile | None


class UnfollowUseCase(UseCase[UnfollowInput, UnfollowResult]):
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def execute(self, input: UnfollowInput, /) -> UnfollowResult:
        """Unfollow an user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        profile = await self._profile_repository.get_by_username(input.username, by=user_id)
        if profile is None:
            LOG.info("could not unfollow profile, profile not found", extra={"input": input})
            return UnfollowResult(None)
        unfollowed_profile = await self._profile_repository.update(
            profile.id,
            UpdateProfileInput(is_following=False),
            by=user_id,
        )
        LOG.info("profile is unfollowed", extra={"input": input, "profile": unfollowed_profile})
        return UnfollowResult(unfollowed_profile)
