__all__ = [
    "AuthToken",
    "AuthTokenGenerator",
    "CreateUserInput",
    "FollowerRepository",
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

from yarl import URL

from conduit.core.entities.common import NotSet

Email = t.NewType("Email", str)
PasswordHash = t.NewType("PasswordHash", str)
RawPassword = t.NewType("RawPassword", str)
UserId = t.NewType("UserId", int)
Username = t.NewType("Username", str)


@dataclass(frozen=True)
class AuthToken:
    v: str

    def __repr__(self) -> str:
        return f"AuthToken('{self.v[:3]}...{self.v[-3:]}')"

    def __str__(self) -> str:
        return self.v


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
    async def get_by_ids(self, ids: t.Collection[UserId]) -> dict[UserId, User]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_username(self, username: Username) -> User | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: UserId, input: UpdateUserInput) -> User | None:
        raise NotImplementedError()


class FollowerRepository(t.Protocol):
    @abc.abstractmethod
    async def follow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def unfollow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def is_followed(self, id: UserId, *, by: UserId) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def are_followed(self, ids: t.Collection[UserId], by: UserId) -> dict[UserId, bool]:
        raise NotImplementedError()


class AuthTokenGenerator(t.Protocol):
    @abc.abstractmethod
    async def generate_token(self, user: User) -> AuthToken:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_user_id(self, token: AuthToken) -> UserId | None:
        raise NotImplementedError()


class PasswordHasher(t.Protocol):
    @abc.abstractmethod
    async def hash_password(self, password: RawPassword) -> PasswordHash:
        raise NotImplementedError()

    @abc.abstractmethod
    async def verify(self, password: RawPassword, hash: PasswordHash) -> bool:
        raise NotImplementedError()
