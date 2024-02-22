__all__ = [
    "GetArticleInput",
    "GetArticleResult",
    "GetArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleSlug, ArticleWithExtra
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.common import (
    get_author,
    get_favorite_count_for_article,
    get_tags_for_article,
    is_favorite,
)
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput
from conduit.core.use_cases.common import get_article, is_user_followed

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetArticleInput(WithOptionalAuthenticationInput):
    slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetArticleResult:
    article: ArticleWithExtra | None


class GetArticleUseCase(UseCase[GetArticleInput, GetArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: GetArticleInput, /) -> GetArticleResult:
        user_id = input.user_id
        article = await get_article(self._unit_of_work, input.slug)
        if article is None:
            return GetArticleResult(None)
        author = await get_author(self._unit_of_work, article.author_id)
        tags = await get_tags_for_article(self._unit_of_work, article.id)
        followed = await is_user_followed(self._unit_of_work, author.id, by=user_id)
        favorite = await is_favorite(self._unit_of_work, article.id, of=user_id)
        favorite_count = await get_favorite_count_for_article(self._unit_of_work, article.id)
        return GetArticleResult(
            ArticleWithExtra(
                v=article,
                author=author,
                tags=tags,
                is_author_followed=followed,
                is_article_favorite=favorite,
                favorite_of_user_count=favorite_count,
            )
        )
