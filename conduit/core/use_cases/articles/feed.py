__all__ = [
    "FeedArticlesInput",
    "FeedArticlesResult",
    "FeedArticlesUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import Article, ArticleFilter, ArticleId, ArticleWithExtra, Tag
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.common import (
    are_favorite,
    get_article_count,
    get_articles,
    get_favorite_count_for_articles,
    get_tags_for_articles,
)
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_users

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeedArticlesInput(WithAuthenticationInput):
    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        # Ensure preconditions
        assert 0 <= self.limit <= 100
        assert self.offset >= 0

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class FeedArticlesResult:
    articles: list[ArticleWithExtra]
    count: int


class FeedArticlesUseCase(UseCase[FeedArticlesInput, FeedArticlesResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: FeedArticlesInput, /) -> FeedArticlesResult:
        """Feed articles.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        filter = ArticleFilter(feed_of=user_id)
        articles = await get_articles(self._unit_of_work, filter, limit=input.limit, offset=input.offset)
        article_count = await get_article_count(self._unit_of_work, filter)
        article_ids = [article.id for article in articles]
        author_ids = {article.author_id for article in articles}
        authors = await get_users(self._unit_of_work, author_ids)
        tags = await get_tags_for_articles(self._unit_of_work, article_ids)
        articles_favorite = await are_favorite(self._unit_of_work, article_ids, of=user_id)
        favorite_count = await get_favorite_count_for_articles(self._unit_of_work, article_ids)
        return FeedArticlesResult(
            articles=self._prepare_articles(
                articles,
                authors,
                tags,
                articles_favorite,
                favorite_count,
            ),
            count=article_count,
        )

    def _prepare_articles(
        self,
        articles: t.Sequence[Article],
        authors: t.Mapping[UserId, User],
        tags: t.Mapping[ArticleId, list[Tag]],
        articles_favorite: t.Mapping[ArticleId, bool],
        favorite_count: t.Mapping[ArticleId, int],
    ) -> list[ArticleWithExtra]:
        result = []
        for article in articles:
            author = authors.get(article.author_id)
            if author is None:
                LOG.error(
                    "author of an article not found",
                    extra={"article_id": article.id, "author_id": article.author_id},
                )
                continue
            result.append(
                ArticleWithExtra(
                    v=article,
                    author=author,
                    tags=tags.get(article.id, []),
                    is_author_followed=True,
                    is_article_favorite=articles_favorite.get(article.id, False),
                    favorite_of_user_count=favorite_count.get(article.id, 0),
                )
            )
        return result
