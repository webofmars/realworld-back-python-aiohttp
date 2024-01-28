__all__ = [
    "CreateArticleInput",
    "CreateArticleResult",
    "CreateArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, field, replace

from conduit.core.entities.article import Article, ArticleRepository, CreateArticleInput as RepositoryCreateArticleInput
from conduit.core.entities.tag import Tag
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateArticleInput(WithAuthenticationInput):
    title: str
    description: str
    body: str
    tags: list[Tag] = field(default_factory=list)

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class CreateArticleResult:
    article: Article


class CreateArticleUseCase(UseCase[CreateArticleInput, CreateArticleResult]):
    def __init__(self, repository: ArticleRepository) -> None:
        self._repository = repository

    async def execute(self, input: CreateArticleInput, /) -> CreateArticleResult:
        """Create a new article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        article = await self._repository.create(
            RepositoryCreateArticleInput(
                title=input.title,
                description=input.description,
                body=input.body,
                tags=self._prepare_tags(input.tags),
            ),
            by=user_id,
        )
        LOG.info("article has been created", extra={"id": article.id, "slug": article.slug})
        return CreateArticleResult(article)

    def _prepare_tags(self, tags: list[Tag]) -> list[Tag]:
        result = []
        seen = set()
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result
