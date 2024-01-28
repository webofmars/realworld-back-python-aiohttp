__all__ = [
    "FeedArticlesInput",
    "FeedArticlesResult",
    "FeedArticlesUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import Article, ArticleFilter, ArticleRepository
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

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
    articles: t.Iterable[Article]
    count: int


class FeedArticlesUseCase(UseCase[FeedArticlesInput, FeedArticlesResult]):
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: FeedArticlesInput, /) -> FeedArticlesResult:
        """Feed articles.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        filter = ArticleFilter(feed_of=user_id)
        count = await self._repository.count(filter)
        LOG.info("got article count", extra={"input": input, "count": count})
        articles = await self._repository.get_many(filter, limit=input.limit, offset=input.offset, by=input.user_id)
        return FeedArticlesResult(articles, count)
