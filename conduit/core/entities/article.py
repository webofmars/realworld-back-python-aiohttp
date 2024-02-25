__all__ = [
    "Article",
    "ArticleFilter",
    "ArticleId",
    "ArticleRepository",
    "ArticleSlug",
    "ArticleWithExtra",
    "CreateArticleInput",
    "FavoriteRepository",
    "Tag",
    "TagRepository",
    "UpdateArticleInput",
]

import abc
import datetime as dt
import typing as t
from dataclasses import dataclass

from conduit.core.entities.common import NotSet
from conduit.core.entities.user import User, UserId, Username

ArticleId = t.NewType("ArticleId", int)
ArticleSlug = t.NewType("ArticleSlug", str)


@dataclass(frozen=True)
class Article:
    id: ArticleId
    author_id: UserId
    slug: ArticleSlug
    title: str
    description: str
    body: str
    created_at: dt.datetime
    updated_at: dt.datetime | None


@dataclass(frozen=True)
class Tag:
    v: str

    def __str__(self) -> str:
        return self.v


@dataclass(frozen=True)
class ArticleWithExtra:
    v: Article
    author: User
    tags: t.Sequence[Tag]
    is_author_followed: bool = False
    is_article_favorite: bool = False
    favorite_of_user_count: int = 0

    def __post_init__(self) -> None:
        assert self.v.author_id == self.author.id


@dataclass(frozen=True)
class CreateArticleInput:
    author_id: UserId
    title: str
    description: str
    body: str


@dataclass(frozen=True)
class ArticleFilter:
    tag: Tag | None = None
    author: Username | None = None
    favorite_of: Username | None = None
    feed_of: UserId | None = None


@dataclass(frozen=True)
class UpdateArticleInput:
    title: str | NotSet = NotSet.NOT_SET
    description: str | NotSet = NotSet.NOT_SET
    body: str | NotSet = NotSet.NOT_SET


class ArticleRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateArticleInput) -> Article:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_many(
        self,
        filter: ArticleFilter,
        *,
        limit: int,
        offset: int,
    ) -> list[Article]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def count(self, filter: ArticleFilter) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_slug(self, slug: ArticleSlug) -> Article | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: ArticleId, input: UpdateArticleInput) -> Article | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: ArticleId) -> ArticleId | None:
        raise NotImplementedError()


class FavoriteRepository(t.Protocol):
    @abc.abstractmethod
    async def add(self, user_id: UserId, article_id: ArticleId) -> int:
        """Adds `article_id` to the favorites of `user_id`.

        Returns:
            The total number of users who have added `article_id` to their favorites.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def remove(self, user_id: UserId, article_id: ArticleId) -> int:
        """Removes `article_id` from the favorites of `user_id`.

        Returns:
            The total number of users who have added `article_id` to their favorites.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def is_favorite(self, article_id: ArticleId, of: UserId) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def are_favorite(self, article_ids: t.Collection[ArticleId], of: UserId) -> dict[ArticleId, bool]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def count(self, article_id: ArticleId) -> int:
        """Counts users who have added `article_id` to their favorites."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def count_many(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, int]:
        raise NotImplementedError()


class TagRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, article_id: ArticleId, tags: t.Collection[Tag]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(self) -> list[Tag]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_for_article(self, article_id: ArticleId) -> list[Tag]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_for_articles(self, article_ids: t.Collection[ArticleId]) -> dict[ArticleId, list[Tag]]:
        raise NotImplementedError()
