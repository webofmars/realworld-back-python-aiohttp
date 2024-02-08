__all__ = [
    "ListArticlesInput",
    "ListArticlesResult",
    "ListArticlesUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import Article, ArticleFilter, ArticleRepository
from conduit.core.entities.tag import Tag
from conduit.core.entities.user import UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class ListArticlesInput(WithOptionalAuthenticationInput):
    tag: Tag | None = None
    author: Username | None = None
    favorite_of: Username | None = None
    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        # Ensure preconditions
        assert 0 <= self.limit <= 100
        assert self.offset >= 0

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)

    def to_filter(self) -> ArticleFilter:
        return ArticleFilter(
            tag=self.tag,
            author=self.author,
            favorite_of=self.favorite_of,
        )


@dataclass(frozen=True)
class ListArticlesResult:
    articles: t.Iterable[Article]
    count: int


class ListArticlesUseCase(UseCase[ListArticlesInput, ListArticlesResult]):
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: ListArticlesInput, /) -> ListArticlesResult:
        filter = input.to_filter()
        count = await self._repository.count(filter)
        LOG.info("got article count", extra={"input": input, "count": count})
        articles = await self._repository.get_many(filter, limit=input.limit, offset=input.offset, by=input.user_id)
        return ListArticlesResult(articles, count)
