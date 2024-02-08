__all__ = [
    "FakeArticleRepository",
    "FakeAuthTokenGenerator",
    "FakePasswordHasher",
    "FakeProfileRepository",
    "FakeUserRepository",
]

import datetime as dt
import typing as t
from dataclasses import replace
from hashlib import md5

import pytest

from conduit.core.entities.article import (
    Article,
    ArticleFilter,
    ArticleId,
    ArticleRepository,
    ArticleSlug,
    CreateArticleInput,
    UpdateArticleInput,
)
from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.profile import Profile, ProfileRepository, UpdateProfileInput
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


class FakeProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self.followers: dict[UserId, set[UserId]] = {}
        self.users: list[User] = []

    async def get_by_username(self, username: Username, by: UserId | None = None) -> Profile | None:
        user = next((u for u in self.users if u.username == username), None)
        if user is None:
            return None
        return Profile(
            id=user.id,
            username=user.username,
            bio=user.bio,
            image=user.image,
            is_following=False if by is None else by in self.followers.get(user.id, set()),
        )

    async def update(self, id: UserId, input: UpdateProfileInput, by: UserId) -> Profile | None:
        user = next((u for u in self.users if u.id == id), None)
        if user is None:
            return None
        if input.is_following is not NotSet.NOT_SET:
            if input.is_following:
                self.followers.setdefault(id, set())
                self.followers[id].add(by)
            else:
                self.followers.setdefault(id, set())
                self.followers[id].discard(by)
        return Profile(
            id=user.id,
            username=user.username,
            bio=user.bio,
            image=user.image,
            is_following=by in self.followers[user.id],
        )


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


class FakeArticleRepository(ArticleRepository):
    def __init__(self, article: t.Optional[Article]) -> None:
        self.article = article
        self.create_input: t.Optional[CreateArticleInput] = None
        self.create_by: t.Optional[UserId] = None
        self.get_many_filter: t.Optional[ArticleFilter] = None
        self.get_many_limit: t.Optional[int] = None
        self.get_many_offset: t.Optional[int] = None
        self.get_many_by: t.Optional[UserId] = None
        self.count_filter: t.Optional[ArticleFilter] = None
        self.get_by_slug_slug: t.Optional[ArticleSlug] = None
        self.get_by_slug_by: t.Optional[UserId] = None
        self.update_id: t.Optional[ArticleId] = None
        self.update_input: t.Optional[UpdateArticleInput] = None
        self.update_by: t.Optional[UserId] = None
        self.delete_id: t.Optional[ArticleId] = None

    async def create(self, input: CreateArticleInput, by: UserId) -> Article:
        self.create_input = input
        self.create_by = by
        assert self.article is not None
        return self.article

    async def get_many(
        self,
        filter: ArticleFilter,
        *,
        limit: int,
        offset: int,
        by: UserId | None = None,
    ) -> t.Iterable[Article]:
        self.get_many_filter = filter
        self.get_many_limit = limit
        self.get_many_offset = offset
        self.get_many_by = by
        return []

    async def count(self, filter: ArticleFilter) -> int:
        self.count_filter = filter
        return 0

    async def get_by_slug(self, slug: ArticleSlug, by: UserId | None = None) -> Article | None:
        self.get_by_slug_slug = slug
        self.get_by_slug_by = by
        return self.article

    async def update(self, id: ArticleId, input: UpdateArticleInput, by: UserId) -> Article | None:
        self.update_id = id
        self.update_input = input
        self.update_by = by
        return None

    async def delete(self, id: ArticleId) -> ArticleId | None:
        self.delete_id = id
        return self.article.id if self.article is not None else None


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def profile_repository() -> FakeProfileRepository:
    return FakeProfileRepository()


@pytest.fixture
def existing_article() -> Article:
    return Article(
        id=ArticleId(1),
        slug=ArticleSlug("test-article-slug"),
        title="test-title",
        description="test-description",
        body="test-body",
        tags=[],
        created_at=dt.datetime.utcnow(),
        updated_at=None,
        is_favorite=False,
        favorite_of_user_count=0,
        author=Profile(
            id=UserId(1),
            username=Username("test-username"),
            bio="",
            image=None,
            is_following=False,
        ),
    )


@pytest.fixture
def article_repository(existing_article: Article) -> FakeArticleRepository:
    return FakeArticleRepository(existing_article)


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def auth_token_generator() -> AuthTokenGenerator:
    return FakeAuthTokenGenerator()


@pytest.fixture
async def existing_user(user_repository: UserRepository) -> User:
    return await user_repository.create(
        CreateUserInput(
            username=Username("test"),
            email=Email("test@test.test"),
            password=PasswordHash("test"),
        )
    )


@pytest.fixture
async def existing_user_auth_token(existing_user: User, auth_token_generator: AuthTokenGenerator) -> AuthToken:
    return await auth_token_generator.generate_token(existing_user)
