__all__ = [
    "Profile",
    "ProfileRepository",
    "UpdateProfileInput",
]

import abc
import typing as t
from dataclasses import dataclass

from yarl import URL

from conduit.core.entities.common import NotSet
from conduit.core.entities.user import UserId, Username


@dataclass(frozen=True)
class Profile:
    id: UserId
    username: Username
    bio: str
    image: URL | None
    is_following: bool


@dataclass(frozen=True)
class UpdateProfileInput:
    is_following: bool | NotSet = NotSet.NOT_SET


class ProfileRepository(t.Protocol):
    @abc.abstractmethod
    async def get_by_username(self, username: Username, by: UserId | None = None) -> Profile | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: UserId, input: UpdateProfileInput, by: UserId) -> Profile | None:
        raise NotImplementedError()
