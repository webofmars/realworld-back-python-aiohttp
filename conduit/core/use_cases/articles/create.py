__all__ = [
    "CreateArticleInput",
    "CreateArticleResult",
    "CreateArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, field, replace

from conduit.core.entities.article import (
    Article,
    ArticleWithExtra,
    CreateArticleInput as RepositoryCreateArticleInput,
    Tag,
)
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId
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
    article: ArticleWithExtra


class CreateArticleUseCase(UseCase[CreateArticleInput, CreateArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: CreateArticleInput, /) -> CreateArticleResult:
        """Create a new article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
        """
        user_id = input.ensure_authenticated()
        author = await self._get_author(user_id)
        article = await self._create_article(input, author.id)
        return CreateArticleResult(
            ArticleWithExtra(
                v=article,
                author=author,
                tags=input.tags,
            )
        )

    async def _get_author(self, user_id: UserId) -> User:
        async with self._unit_of_work.begin() as uow:
            author = await uow.users.get_by_id(user_id)
        if author is None:
            LOG.info("could not find user by id", extra={"user_id": user_id})
            raise UserIsNotAuthenticatedError()
        return author

    async def _create_article(self, input: CreateArticleInput, author_id: UserId) -> Article:
        async with self._unit_of_work.begin() as uow:
            article = await uow.articles.create(
                RepositoryCreateArticleInput(
                    author_id=author_id,
                    title=input.title,
                    description=input.description,
                    body=input.body,
                ),
            )
            await uow.tags.create(article.id, input.tags)
        LOG.info("article has been created", extra={"id": article.id, "slug": article.slug, "tags": input.tags})
        return article
