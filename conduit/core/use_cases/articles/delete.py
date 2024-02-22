__all__ = [
    "DeleteArticleInput",
    "DeleteArticleResult",
    "DeleteArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleId, ArticleSlug
from conduit.core.entities.errors import PermissionDeniedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_article

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteArticleInput(WithAuthenticationInput):
    slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class DeleteArticleResult:
    id: ArticleId | None


class DeleteArticleUseCase(UseCase[DeleteArticleInput, DeleteArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: DeleteArticleInput, /) -> DeleteArticleResult:
        """Delete an existing article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            PermissionDeniedError: If user is not allowed to delete the article.
        """
        user_id = input.ensure_authenticated()
        article = await get_article(self._unit_of_work, input.slug)
        if article is None:
            return DeleteArticleResult(None)
        if article.author_id != user_id:
            LOG.info(
                "user is not allowed to delete the article",
                extra={"user_id": user_id, "author_id": article.author_id},
            )
            raise PermissionDeniedError()
        deleted_article_id = await self._delete_article(article.id)
        return DeleteArticleResult(deleted_article_id)

    async def _delete_article(self, article_id: ArticleId) -> ArticleId | None:
        async with self._unit_of_work.begin() as uow:
            deleted_article_id = await uow.articles.delete(article_id)
        LOG.info("article has been deleted", extra={"article_id": deleted_article_id})
        return deleted_article_id
