__all__ = [
    "GetArticleInput",
    "GetArticleResult",
    "GetArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import Article, ArticleRepository, ArticleSlug
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetArticleInput(WithOptionalAuthenticationInput):
    slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetArticleResult:
    article: Article | None


class GetArticleUseCase(UseCase[GetArticleInput, GetArticleResult]):
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: GetArticleInput, /) -> GetArticleResult:
        article = await self._repository.get_by_slug(input.slug, by=input.user_id)
        if article is None:
            LOG.info("article not found", extra={"input": input})
            return GetArticleResult(None)
        LOG.info("got article", extra={"input": input, "article_id": article.id})
        return GetArticleResult(article)
