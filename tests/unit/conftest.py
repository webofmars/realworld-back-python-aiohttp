__all__ = [
    "FakeArticleRepository",
    "FakeAuthTokenGenerator",
    "FakeCommentRepository",
    "FakeFavoriteRepository",
    "FakeFollowerRepository",
    "FakePasswordHasher",
    "FakeTagRepository",
    "FakeUnitOfWork",
    "FakeUserRepository",
]

import datetime as dt
import typing as t
from contextlib import asynccontextmanager
from dataclasses import dataclass
from hashlib import md5
from itertools import chain

import pytest
from yarl import URL

from conduit.core.entities.article import (
    Article,
    ArticleFilter,
    ArticleId,
    ArticleRepository,
    ArticleSlug,
    CreateArticleInput,
    FavoriteRepository,
    Tag,
    TagRepository,
    UpdateArticleInput,
)
from conduit.core.entities.comment import Comment, CommentFilter, CommentId, CommentRepository, CreateCommentInput
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import (
    AuthToken,
    AuthTokenGenerator,
    CreateUserInput,
    Email,
    FollowerRepository,
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
    def __init__(self, user: User) -> None:
        self.user: User | None = user
        self.create_input: CreateUserInput | None = None
        self.create_error: Exception | None = None
        self.get_by_email_email: Email | None = None
        self.get_by_id_id: UserId | None = None
        self.get_by_username_username: Username | None = None
        self.update_id: UserId | None = None
        self.update_input: UpdateUserInput | None = None
        self.update_error: Exception | None = None
        self.get_by_ids_ids: t.Collection[UserId] | None = None

    async def create(self, input: CreateUserInput) -> User:
        self.create_input = input
        if self.create_error is not None:
            raise self.create_error
        assert self.user is not None
        return self.user

    async def get_by_email(self, email: Email) -> User | None:
        self.get_by_email_email = email
        return self.user

    async def get_by_id(self, id: UserId) -> User | None:
        self.get_by_id_id = id
        return self.user

    async def get_by_username(self, username: Username) -> User | None:
        self.get_by_username_username = username
        return self.user

    async def get_by_ids(self, ids: t.Collection[UserId]) -> dict[UserId, User]:
        self.get_by_ids_ids = ids
        if self.user is None:
            return {}
        return {self.user.id: self.user}

    async def update(self, id: UserId, input: UpdateUserInput) -> User | None:
        self.update_id = id
        self.update_input = input
        if self.update_error is not None:
            raise self.update_error
        return self.user


class FakeFollowerRepository(FollowerRepository):
    def __init__(self) -> None:
        self.followers: dict[UserId, set[UserId]] = {}

    async def follow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        self.followers.setdefault(followed_id, set())
        self.followers[followed_id].add(follower_id)

    async def unfollow(self, *, follower_id: UserId, followed_id: UserId) -> None:
        self.followers.setdefault(followed_id, set())
        self.followers[followed_id].discard(follower_id)

    async def is_followed(self, id: UserId, *, by: UserId) -> bool:
        return by in self.followers.get(id, set())

    async def are_followed(self, ids: t.Collection[UserId], by: UserId) -> dict[UserId, bool]:
        return {id: await self.is_followed(id, by=by) for id in ids}


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
        self.get_many_filter: t.Optional[ArticleFilter] = None
        self.get_many_limit: t.Optional[int] = None
        self.get_many_offset: t.Optional[int] = None
        self.count_filter: t.Optional[ArticleFilter] = None
        self.get_by_slug_slug: t.Optional[ArticleSlug] = None
        self.update_id: t.Optional[ArticleId] = None
        self.update_input: t.Optional[UpdateArticleInput] = None
        self.delete_id: t.Optional[ArticleId] = None

    async def create(self, input: CreateArticleInput) -> Article:
        self.create_input = input
        assert self.article is not None
        return self.article

    async def get_many(
        self,
        filter: ArticleFilter,
        *,
        limit: int,
        offset: int,
    ) -> list[Article]:
        self.get_many_filter = filter
        self.get_many_limit = limit
        self.get_many_offset = offset
        return []

    async def count(self, filter: ArticleFilter) -> int:
        self.count_filter = filter
        return 0

    async def get_by_slug(self, slug: ArticleSlug) -> Article | None:
        self.get_by_slug_slug = slug
        return self.article

    async def update(self, id: ArticleId, input: UpdateArticleInput) -> Article | None:
        self.update_id = id
        self.update_input = input
        return self.article

    async def delete(self, id: ArticleId) -> ArticleId | None:
        self.delete_id = id
        return self.article.id if self.article is not None else None


class FakeFavoriteRepository(FavoriteRepository):
    def __init__(self) -> None:
        self.favorites: dict[ArticleId, set[UserId]] = {}

    async def add(self, user_id: UserId, article_id: ArticleId) -> int:
        self.favorites.setdefault(article_id, set())
        self.favorites[article_id].add(user_id)
        return len(self.favorites[article_id])

    async def remove(self, user_id: UserId, article_id: ArticleId) -> int:
        self.favorites.setdefault(article_id, set())
        self.favorites[article_id].discard(user_id)
        return len(self.favorites[article_id])

    async def is_favorite(self, article_id: ArticleId, of: UserId) -> bool:
        return of in self.favorites.get(article_id, set())

    async def are_favorite(self, article_ids: t.Collection[ArticleId], of: UserId) -> dict[ArticleId, bool]:
        return {article_id: await self.is_favorite(article_id, of) for article_id in article_ids}

    async def count(self, article_id: ArticleId) -> int:
        return len(self.favorites.get(article_id, set()))

    async def count_many(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, int]:
        return {article_id: await self.count(article_id) for article_id in article_ids}


class FakeTagRepository(TagRepository):
    def __init__(self) -> None:
        self.tags: dict[ArticleId, list[Tag]] = {}

    async def create(self, article_id: ArticleId, tags: t.Collection[Tag]) -> None:
        self.tags[article_id] = list(tags)

    async def get_all(self) -> list[Tag]:
        return list(chain.from_iterable(self.tags.values()))

    async def get_for_article(self, article_id: ArticleId) -> list[Tag]:
        return self.tags.get(article_id, [])

    async def get_for_articles(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, list[Tag]]:
        return {article_id: await self.get_for_article(article_id) for article_id in article_ids}


class FakeCommentRepository(CommentRepository):
    def __init__(self, comment: Comment) -> None:
        self.comment: t.Optional[Comment] = comment
        self.create_input: t.Optional[CreateCommentInput] = None
        self.get_many_filter: t.Optional[CommentFilter] = None
        self.get_by_id_id: t.Optional[CommentId] = None
        self.delete_id: t.Optional[CommentId] = None

    async def create(self, input: CreateCommentInput) -> Comment:
        self.create_input = input
        assert self.comment is not None
        return self.comment

    async def get_many(self, filter: CommentFilter) -> list[Comment]:
        self.get_many_filter = filter
        return []

    async def get_by_id(self, id: CommentId) -> Comment | None:
        self.get_by_id_id = id
        return self.comment

    async def delete(self, id: CommentId) -> CommentId | None:
        self.delete_id = id
        return id


class FakeUnitOfWork(UnitOfWork):
    @dataclass(frozen=True)
    class Context:
        users: FakeUserRepository
        followers: FakeFollowerRepository
        articles: FakeArticleRepository
        tags: FakeTagRepository
        favorites: FakeFavoriteRepository
        comments: FakeCommentRepository

    def __init__(
        self,
        user_repository: FakeUserRepository,
        follower_repository: FakeFollowerRepository,
        article_repository: FakeArticleRepository,
        tag_repository: FakeTagRepository,
        favorite_repository: FakeFavoriteRepository,
        comment_repository: FakeCommentRepository,
    ) -> None:
        self.user_repository = user_repository
        self.follower_repository = follower_repository
        self.article_repository = article_repository
        self.tag_repository = tag_repository
        self.favorite_repository = favorite_repository
        self.comment_repository = comment_repository

    @asynccontextmanager
    async def begin(self) -> t.AsyncIterator[Context]:
        yield self.Context(
            users=self.user_repository,
            followers=self.follower_repository,
            articles=self.article_repository,
            tags=self.tag_repository,
            favorites=self.favorite_repository,
            comments=self.comment_repository,
        )


@pytest.fixture
async def existing_user() -> User:
    return User(
        id=UserId(1),
        username=Username("test"),
        email=Email("test@test.test"),
        password=PasswordHash("test-password-hash"),
        bio="test-bio",
        image=URL("https://test.test/test.jpg"),
    )


@pytest.fixture
async def existing_user_auth_token(existing_user: User, auth_token_generator: AuthTokenGenerator) -> AuthToken:
    return await auth_token_generator.generate_token(existing_user)


@pytest.fixture
def existing_article() -> Article:
    return Article(
        id=ArticleId(1),
        slug=ArticleSlug("test-article-slug"),
        title="test-title",
        description="test-description",
        body="test-body",
        created_at=dt.datetime.utcnow(),
        updated_at=None,
        author_id=UserId(1),
    )


@pytest.fixture
def existing_comment(existing_article: Article) -> Comment:
    return Comment(
        id=CommentId(1),
        created_at=dt.datetime.utcnow(),
        updated_at=None,
        body="test",
        author_id=UserId(1),
        article_id=existing_article.id,
    )


@pytest.fixture
def user_repository(existing_user: User) -> FakeUserRepository:
    return FakeUserRepository(existing_user)


@pytest.fixture
def follower_repository() -> FakeFollowerRepository:
    return FakeFollowerRepository()


@pytest.fixture
def article_repository(existing_article: Article) -> FakeArticleRepository:
    return FakeArticleRepository(existing_article)


@pytest.fixture
def favorite_repository() -> FakeFavoriteRepository:
    return FakeFavoriteRepository()


@pytest.fixture
def tag_repository() -> FakeTagRepository:
    return FakeTagRepository()


@pytest.fixture
def comment_repository(existing_comment: Comment) -> FakeCommentRepository:
    return FakeCommentRepository(existing_comment)


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def auth_token_generator() -> AuthTokenGenerator:
    return FakeAuthTokenGenerator()


@pytest.fixture
def unit_of_work(
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    article_repository: FakeArticleRepository,
    favorite_repository: FakeFavoriteRepository,
    tag_repository: FakeTagRepository,
    comment_repository: FakeCommentRepository,
) -> FakeUnitOfWork:
    return FakeUnitOfWork(
        user_repository,
        follower_repository,
        article_repository,
        tag_repository,
        favorite_repository,
        comment_repository,
    )
