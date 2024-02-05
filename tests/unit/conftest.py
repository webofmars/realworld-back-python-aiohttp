__all__ = [
    "FakeAuthTokenGenerator",
    "FakePasswordHasher",
    "FakeUserRepository",
]

from dataclasses import replace
from hashlib import md5

import pytest

from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.user import (
    AuthToken,
    AuthTokenGenerator,
    CreateUserInput,
    Email,
    PasswordHash,
    PasswordHasher,
    RawPassword,
    UpdateUserInput,
    User,
    UserId,
    Username,
    UserRepository,
)


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: list[User] = []
        self.usernames: set[Username] = set()
        self.emails: set[Email] = set()

    async def create(self, input: CreateUserInput) -> User:
        if input.username in self.usernames:
            raise UsernameAlreadyExistsError()
        if input.email in self.emails:
            raise EmailAlreadyExistsError()
        new_user = User(
            id=UserId(len(self.users) + 1),
            username=input.username,
            email=input.email,
            password=input.password,
            bio="",
            image=None,
        )
        self.users.append(new_user)
        self.usernames.add(new_user.username)
        self.emails.add(new_user.email)
        return new_user

    async def get_by_email(self, email: Email) -> User | None:
        for user in self.users:
            if user.email == email:
                return user
        return None

    async def get_by_id(self, id: UserId) -> User | None:
        for user in self.users:
            if user.id == id:
                return user
        return None

    async def update(self, id: UserId, input: UpdateUserInput) -> User | None:
        ix: int | None = None
        user: User | None = None
        for i, u in enumerate(self.users):
            if u.id == id:
                user = u
                ix = i
                break
        if user is None or ix is None:
            return None
        if input.username is not NotSet.NOT_SET:
            if input.username in self.usernames:
                raise UsernameAlreadyExistsError()
            self.usernames.remove(user.username)
            user = replace(user, username=input.username)
        if input.email is not NotSet.NOT_SET:
            if input.email in self.emails:
                raise EmailAlreadyExistsError()
            self.emails.remove(user.email)
            user = replace(user, email=input.email)
        if input.password is not NotSet.NOT_SET:
            user = replace(user, password=input.password)
        if input.bio is not NotSet.NOT_SET:
            user = replace(user, bio=input.bio)
        if input.image is not NotSet.NOT_SET:
            user = replace(user, image=input.image)
        self.users[ix] = user
        return user


class FakePasswordHasher(PasswordHasher):
    async def hash_password(self, password: RawPassword) -> PasswordHash:
        return PasswordHash(md5(password.encode()).hexdigest())

    async def verify(self, password: RawPassword, hash: PasswordHash) -> bool:
        return await self.hash_password(password) == hash


class FakeAuthTokenGenerator(AuthTokenGenerator):
    def __init__(self) -> None:
        self.tokens: dict[AuthToken, UserId] = {}

    async def generate_token(self, user: User) -> AuthToken:
        token = AuthToken(f"test-token-{user.id}")
        self.tokens[token] = user.id
        return token

    async def get_user_id(self, token: AuthToken) -> UserId | None:
        return self.tokens.get(token)


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def auth_token_generator() -> AuthTokenGenerator:
    return FakeAuthTokenGenerator()
