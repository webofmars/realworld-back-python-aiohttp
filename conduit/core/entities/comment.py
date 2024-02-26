__all__ = [
    "Comment",
    "CommentFilter",
    "CommentId",
    "CommentRepository",
    "CommentWithExtra",
    "CreateCommentInput",
]

import abc
import datetime as dt
import typing as t
from dataclasses import dataclass

from conduit.core.entities.article import ArticleId
from conduit.core.entities.user import User, UserId

CommentId = t.NewType("CommentId", int)


@dataclass(frozen=True)
class Comment:
    id: CommentId
    author_id: UserId
    article_id: ArticleId
    created_at: dt.datetime
    updated_at: t.Optional[dt.datetime]
    body: str


@dataclass(frozen=True)
class CommentWithExtra:
    v: Comment
    author: User
    is_author_followed: bool

    def __post_init__(self) -> None:
        assert self.v.author_id == self.author.id


@dataclass(frozen=True)
class CreateCommentInput:
    author_id: UserId
    article_id: ArticleId
    body: str


@dataclass(frozen=True)
class CommentFilter:
    article_id: ArticleId | None = None


class CommentRepository(t.Protocol):
    @abc.abstractmethod
    async def create(self, input: CreateCommentInput) -> Comment:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_many(self, filter: CommentFilter) -> list[Comment]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_id(self, id: CommentId) -> Comment | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: CommentId) -> CommentId | None:
        raise NotImplementedError()
