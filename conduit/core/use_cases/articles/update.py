__all__ = [
    "UpdateArticleInput",
    "UpdateArticleResult",
    "UpdateArticleUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.article import (
    Article,
    ArticleId,
    ArticleSlug,
    ArticleWithExtra,
    UpdateArticleInput as RepositoryUpdateArticleInput,
)
from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import PermissionDeniedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.common import (
    get_author,
    get_favorite_count_for_article,
    get_tags_for_article,
    is_favorite,
)
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_article, is_user_followed

LOG = structlog.get_logger(__name__)


@dataclass(frozen=True)
class UpdateArticleInput(WithAuthenticationInput):
    slug: ArticleSlug
    title: str | NotSet = NotSet.NOT_SET
    description: str | NotSet = NotSet.NOT_SET
    body: str | NotSet = NotSet.NOT_SET

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class UpdateArticleResult:
    article: ArticleWithExtra | None


class UpdateArticleUseCase(UseCase[UpdateArticleInput, UpdateArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: UpdateArticleInput, /) -> UpdateArticleResult:
        """Update an existing article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            PermissionDeniedError: If user is not allowed to update the article.
        """
        user_id = input.ensure_authenticated()
        article = await get_article(self._unit_of_work, input.slug)
        if article is None:
            return UpdateArticleResult(None)
        if article.author_id != user_id:
            LOG.info("user is not allowed to update article", input=input)
            raise PermissionDeniedError()
        author = await get_author(self._unit_of_work, article.author_id)
        tags = await get_tags_for_article(self._unit_of_work, article.id)
        author_followed = await is_user_followed(self._unit_of_work, author.id, by=user_id)
        favorite = await is_favorite(self._unit_of_work, article.id, of=user_id)
        favorite_count = await get_favorite_count_for_article(self._unit_of_work, article.id)
        updated_article = await self._update_article(article.id, input)
        if updated_article is None:
            return UpdateArticleResult(None)
        return UpdateArticleResult(
            ArticleWithExtra(
                v=updated_article,
                author=author,
                tags=tags,
                is_author_followed=author_followed,
                is_article_favorite=favorite,
                favorite_of_user_count=favorite_count,
            )
        )

    async def _update_article(self, article_id: ArticleId, input: UpdateArticleInput) -> Article | None:
        async with self._unit_of_work.begin() as uow:
            updated_article = await uow.articles.update(
                article_id,
                RepositoryUpdateArticleInput(
                    title=input.title,
                    description=input.description,
                    body=input.body,
                ),
            )
        LOG.info("article has been updated", id=updated_article.id if updated_article is not None else None)
        return updated_article
