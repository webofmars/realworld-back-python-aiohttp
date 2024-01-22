__all__ = [
    "AuthToken",
    "AuthTokenGenerator",
    "CreateUserInput",
    "PasswordHasher",
    "User",
    "UserRepository",
    "Username",
]

import abc
import typing as t
from dataclasses import dataclass
from enum import Enum

from yarl import URL

from conduit.core.entities.common import Email, PasswordHash, RawPassword, Username

AuthToken = t.NewType("AuthToken", str)
UserId = t.NewType("UserId", int)


@dataclass(frozen=True)
class User:
    id: UserId
    username: Username
    email: Email
    password: PasswordHash
    bio: str
    image: URL | None


@dataclass(frozen=True)
class CreateUserInput:
    username: Username
    email: Email
    password: PasswordHash


class UserRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateUserInput) -> User:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        raise NotImplementedError()


class AuthTokenGenerator(t.Protocol):
    @abc.abstractmethod
    async def generate_token(self, user: User) -> AuthToken:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_user_info(self, token: AuthToken) -> User | None:
        raise NotImplementedError()


class PasswordHasher(t.Protocol):
    class Verification(Enum):
        SUCCESS = 1
        FAIL = 2

    @abc.abstractmethod
    async def hash_password(self, password: RawPassword) -> PasswordHash:
        raise NotImplementedError()

    @abc.abstractmethod
    async def verify(self, password: RawPassword, hash: PasswordHash) -> Verification:
        raise NotImplementedError()
