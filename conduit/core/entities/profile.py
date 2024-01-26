__all__ = [
    "Profile",
    "ProfileRepository",
]

import abc
import typing as t
from dataclasses import dataclass

from yarl import URL

from conduit.core.entities.user import UserId, Username


@dataclass(frozen=True)
class Profile:
    username: Username
    bio: str
    image: URL | None
    is_following: bool


class ProfileRepository(t.Protocol):
    @abc.abstractmethod
    async def get(self, username: Username, is_following_by: UserId | None = None) -> t.Optional[Profile]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def follow(self, username: Username, following_by: UserId) -> Profile | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def unfollow(self, username: Username, following_by: UserId) -> Profile | None:
        raise NotImplementedError()
