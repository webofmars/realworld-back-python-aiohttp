__all__ = [
    "AuthToken",
    "Username",
]

import abc
import typing as t
from dataclasses import dataclass

from yarl import URL

from conduit.core.entities.common import Email, PasswordHash, Username

AuthToken = t.NewType("AuthToken", str)


@dataclass(frozen=True)
class User:
    username: Username
    password: PasswordHash
    email: Email
    token: AuthToken
    bio: str
    image: URL | None


class UserRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, user: User) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        raise NotImplementedError()
