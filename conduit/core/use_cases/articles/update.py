__all__ = [
    "UpdateArticleInput",
    "UpdateArticleResult",
    "UpdateArticleUseCase",
]
import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import (
    Article,
    ArticleRepository,
    ArticleSlug,
    UpdateArticleInput as RepositoryUpdateArticleInput,
)
from conduit.core.entities.common import NotSet
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


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
    article: Article | None


class UpdateArticleUseCase(UseCase[UpdateArticleInput, UpdateArticleResult]):
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: UpdateArticleInput, /) -> UpdateArticleResult:
        """Update an existing article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        updated_article = await self._repository.update(
            input.slug,
            RepositoryUpdateArticleInput(
                title=input.title,
                description=input.description,
                body=input.body,
            ),
            by=user_id,
        )
        if updated_article is None:
            LOG.info("could not update article", extra={"slug": input.slug, "user_id": user_id})
        else:
            LOG.info("article has been updated", extra={"id": updated_article.id, "slug": updated_article.slug})
        return UpdateArticleResult(updated_article)
