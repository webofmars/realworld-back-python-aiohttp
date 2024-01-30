__all__ = [
    "UnfavoriteArticleInput",
    "UnfavoriteArticleResult",
    "UnfavoriteArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import Article, ArticleRepository, ArticleSlug, UpdateArticleInput
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UnfavoriteArticleInput(WithAuthenticationInput):
    slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UnfavoriteArticleResult:
    article: Article | None


class UnfavoriteArticleUseCase(UseCase[UnfavoriteArticleInput, UnfavoriteArticleResult]):
    def __init__(self, article_repository: ArticleRepository) -> None:
        self._article_repository = article_repository

    async def execute(self, input: UnfavoriteArticleInput, /) -> UnfavoriteArticleResult:
        """Remove an article from user's favorites.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        article = await self._article_repository.get_by_slug(input.slug)
        if article is None:
            LOG.info("could not remove article from favorites, article not found", extra={"input": input})
            return UnfavoriteArticleResult(None)
        unfavorite_article = await self._article_repository.update(
            article.id,
            UpdateArticleInput(is_favorite=False),
            by=user_id,
        )
        LOG.info("article has been removed from favorites", extra={"input": input})
        return UnfavoriteArticleResult(unfavorite_article)
