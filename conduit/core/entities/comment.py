__all__ = [
    "Comment",
    "CommentFilter",
    "CommentId",
    "CommentRepository",
    "CreateCommentInput",
]

import abc
import datetime as dt
import typing as t
from dataclasses import dataclass

from conduit.core.entities.article import ArticleId, ArticleSlug
from conduit.core.entities.profile import Profile
from conduit.core.entities.user import UserId

CommentId = t.NewType("CommentId", int)


@dataclass(frozen=True)
class Comment:
    id: CommentId
    created_at: dt.datetime
    updated_at: dt.datetime
    body: str
    author: Profile


@dataclass(frozen=True)
class CreateCommentInput:
    article_id: ArticleId
    body: str


@dataclass(frozen=True)
class CommentFilter:
    article_slug: ArticleSlug | None = None


class CommentRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateCommentInput, by: UserId) -> Comment:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_many(self, filter: CommentFilter, by: UserId | None = None) -> t.Iterable[Comment]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_id(self, id: CommentId, by: UserId | None = None) -> Comment | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: CommentId) -> CommentId | None:
        raise NotImplementedError()
