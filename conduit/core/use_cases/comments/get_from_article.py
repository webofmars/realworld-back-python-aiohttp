__all__ = [
    "GetCommentsFromArticleInput",
    "GetCommentsFromArticleResult",
    "GetCommentsFromArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import Comment, CommentFilter, CommentRepository
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetCommentsFromArticleInput(WithOptionalAuthenticationInput):
    article_slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetCommentsFromArticleResult:
    comments: t.Iterable[Comment]


class GetCommentsFromArticleUseCase(UseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult]):
    def __init__(self, repository: CommentRepository) -> None:
        self._repository = repository

    async def execute(self, input: GetCommentsFromArticleInput, /) -> GetCommentsFromArticleResult:
        comments = await self._repository.get_many(CommentFilter(input.article_slug), by=input.user_id)
        LOG.info("got comments from the article", extra={"input": input})
        return GetCommentsFromArticleResult(comments)
