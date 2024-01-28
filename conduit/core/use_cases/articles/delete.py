__all__ = [
    "DeleteArticleInput",
    "DeleteArticleResult",
    "DeleteArticleUseCase",
]

import logging
from dataclasses import dataclass

from conduit.core.entities.article import ArticleId, ArticleRepository, ArticleSlug
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteArticleInput(WithAuthenticationInput):
    slug: ArticleSlug


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
        """
        user_id = input.ensure_authenticated()
        deleted_article_id = await self._repository.delete(input.slug, user_id)
        if deleted_article_id is None:
            LOG.info("could not delete article", extra={"input": input})
        else:
            LOG.info("article has been deleted", extra={"id": deleted_article_id, "input": input})
        return DeleteArticleResult(deleted_article_id)
