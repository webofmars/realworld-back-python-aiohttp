__all__ = [
    "UnfavoriteArticleInput",
    "UnfavoriteArticleResult",
    "UnfavoriteArticleUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.article import ArticleId, ArticleSlug, ArticleWithExtra
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.common import get_author, get_tags_for_article
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_article, is_user_followed

LOG = structlog.get_logger(__name__)


@dataclass(frozen=True)
class UnfavoriteArticleInput(WithAuthenticationInput):
    slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UnfavoriteArticleResult:
    article: ArticleWithExtra | None


class UnfavoriteArticleUseCase(UseCase[UnfavoriteArticleInput, UnfavoriteArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: UnfavoriteArticleInput, /) -> UnfavoriteArticleResult:
        """Removes an article from user's favorites.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        article = await get_article(self._unit_of_work, input.slug)
        if article is None:
            return UnfavoriteArticleResult(None)
        author = await get_author(self._unit_of_work, article.author_id)
        tags = await get_tags_for_article(self._unit_of_work, article.id)
        followed = await is_user_followed(self._unit_of_work, author.id, by=user_id)
        favorite_of_user_count = await self._remove_from_favorites(user_id, article.id)
        return UnfavoriteArticleResult(
            ArticleWithExtra(
                v=article,
                author=author,
                tags=tags,
                is_author_followed=followed,
                is_article_favorite=False,
                favorite_of_user_count=favorite_of_user_count,
            )
        )

    async def _remove_from_favorites(self, user_id: UserId, article_id: ArticleId) -> int:
        async with self._unit_of_work.begin() as uow:
            favorite_of_user_count = await uow.favorites.remove(user_id, article_id)
        LOG.info(
            "article has been removed from favorites",
            user_id=user_id,
            article_id=article_id,
            favorite_of_user_count=favorite_of_user_count,
        )
        return favorite_of_user_count
