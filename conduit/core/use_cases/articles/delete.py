__all__ = [
    "DeleteArticleInput",
    "DeleteArticleResult",
    "DeleteArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleId, ArticleRepository, ArticleSlug
from conduit.core.entities.errors import PermissionDeniedError
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

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
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: DeleteArticleInput, /) -> DeleteArticleResult:
        """Delete an existing article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            PermissionDeniedError: If user is not allowed to delete the article.
        """
        user_id = input.ensure_authenticated()
        article = await self._repository.get_by_slug(input.slug)
        if article is None:
            LOG.info("could not delete article, article not found", extra={"input": input})
            return DeleteArticleResult(None)
        if article.author.id != user_id:
            LOG.info("user is not allowed to delete the article", extra={"input": input})
            raise PermissionDeniedError()
        deleted_article_id = await self._repository.delete(article.id)
        LOG.info("article has been deleted", extra={"input": input})
        return DeleteArticleResult(deleted_article_id)
