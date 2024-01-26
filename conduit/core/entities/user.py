__all__ = [
    "AuthToken",
    "AuthTokenGenerator",
    "CreateUserInput",
    "Email",
    "PasswordHash",
    "PasswordHasher",
    "RawPassword",
    "UpdateUserInput",
    "User",
    "UserId",
    "UserRepository",
    "Username",
]

import abc
import typing as t
from dataclasses import dataclass
from enum import Enum

from yarl import URL

from conduit.core.entities.common import NotSet

AuthToken = t.NewType("AuthToken", str)
Email = t.NewType("Email", str)
PasswordHash = t.NewType("PasswordHash", str)
RawPassword = t.NewType("RawPassword", str)
UserId = t.NewType("UserId", int)
Username = t.NewType("Username", str)


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


@dataclass(frozen=True)
class UpdateUserInput:
    username: Username | NotSet = NotSet.NOT_SET
    email: Email | NotSet = NotSet.NOT_SET
    password: PasswordHash | NotSet = NotSet.NOT_SET
    bio: str | NotSet = NotSet.NOT_SET
    image: URL | None | NotSet = NotSet.NOT_SET


class UserRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateUserInput) -> User:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_id(self, id: UserId) -> User | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: UserId, input: UpdateUserInput) -> User | None:
        raise NotImplementedError()


class AuthTokenGenerator(t.Protocol):
    @abc.abstractmethod
    async def generate_token(self, user: User) -> AuthToken:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_user_id(self, token: AuthToken) -> UserId | None:
        raise NotImplementedError()


class PasswordHasher(t.Protocol):
    class VerificationResult(Enum):
        SUCCESS = 1
        FAIL = 2

        @property
        def is_success(self) -> bool:
            return self is PasswordHasher.VerificationResult.SUCCESS

    @abc.abstractmethod
    async def hash_password(self, password: RawPassword) -> PasswordHash:
        raise NotImplementedError()

    @abc.abstractmethod
    async def verify(self, password: RawPassword, hash: PasswordHash) -> VerificationResult:
        raise NotImplementedError()
