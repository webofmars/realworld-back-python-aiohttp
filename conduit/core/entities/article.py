__all__ = [
    "Article",
    "ArticleId",
    "ArticleRepository",
    "ArticleSlug",
    "ArticleFilter",
    "CreateArticleInput",
    "UpdateArticleInput",
]

import abc
import datetime as dt
import typing as t
from dataclasses import dataclass

from conduit.core.entities.common import NotSet
from conduit.core.entities.profile import Profile
from conduit.core.entities.tag import Tag
from conduit.core.entities.user import UserId, Username

ArticleId = t.NewType("ArticleId", int)
ArticleSlug = t.NewType("ArticleSlug", str)


@dataclass(frozen=True)
class Article:
    id: ArticleId
    slug: ArticleSlug
    title: str
    description: str
    body: str
    tags: list[Tag]
    created_at: dt.datetime
    updated_at: dt.datetime | None
    is_favorite: bool
    favorite_of_user_count: int
    author: Profile


@dataclass(frozen=True)
class CreateArticleInput:
    title: str
    description: str
    body: str
    tags: list[Tag]


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
    is_favorite: bool | NotSet = NotSet.NOT_SET


class ArticleRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateArticleInput, by: UserId) -> Article:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_many(
        self,
        filter: ArticleFilter,
        *,
        limit: int,
        offset: int,
        by: UserId | None = None,
    ) -> t.Iterable[Article]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def count(self, filter: ArticleFilter) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_slug(self, slug: ArticleSlug, by: UserId | None = None) -> Article | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self, id: ArticleId, input: UpdateArticleInput, by: UserId) -> Article | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: ArticleId) -> ArticleId | None:
        raise NotImplementedError()
