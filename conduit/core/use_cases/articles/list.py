__all__ = [
    "ListArticlesInput",
    "ListArticlesResult",
    "ListArticlesUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.article import Article, ArticleFilter, ArticleId, ArticleWithExtra, Tag
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.common import (
    are_favorite,
    get_article_count,
    get_articles,
    get_favorite_count_for_articles,
    get_tags_for_articles,
)
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput
from conduit.core.use_cases.common import are_users_followed, get_users

LOG = structlog.get_logger(__name__)


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
    articles: t.List[ArticleWithExtra]
    count: int


class ListArticlesUseCase(UseCase[ListArticlesInput, ListArticlesResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: ListArticlesInput, /) -> ListArticlesResult:
        user_id = input.user_id
        filter = input.to_filter()
        articles = await get_articles(self._unit_of_work, filter, limit=input.limit, offset=input.offset)
        article_count = await get_article_count(self._unit_of_work, filter)
        article_ids = [article.id for article in articles]
        author_ids = {article.author_id for article in articles}
        authors = await get_users(self._unit_of_work, author_ids)
        authors_followed = await are_users_followed(self._unit_of_work, author_ids, by=user_id)
        tags = await get_tags_for_articles(self._unit_of_work, article_ids)
        articles_favorite = await are_favorite(self._unit_of_work, article_ids, of=user_id)
        favorite_count = await get_favorite_count_for_articles(self._unit_of_work, article_ids)
        return ListArticlesResult(
            self._prepare_articles(
                articles,
                authors,
                authors_followed,
                tags,
                articles_favorite,
                favorite_count,
            ),
            article_count,
        )

    def _prepare_articles(
        self,
        articles: t.Sequence[Article],
        authors: t.Mapping[UserId, User],
        authors_followed: t.Mapping[UserId, bool],
        tags: t.Mapping[ArticleId, list[Tag]],
        articles_favorite: t.Mapping[ArticleId, bool],
        favorite_count: t.Mapping[ArticleId, int],
    ) -> list[ArticleWithExtra]:
        result = []
        for article in articles:
            author = authors.get(article.author_id)
            if author is None:
                LOG.error("author of an article not found", article_id=article.id, author_id=article.author_id)
                continue
            result.append(
                ArticleWithExtra(
                    v=article,
                    author=author,
                    tags=tags.get(article.id, []),
                    is_author_followed=authors_followed.get(author.id, False),
                    is_article_favorite=articles_favorite.get(article.id, False),
                    favorite_of_user_count=favorite_count.get(article.id, 0),
                )
            )
        return result
