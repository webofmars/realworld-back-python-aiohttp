__all__ = [
    "AddCommentToArticleInput",
    "AddCommentToArticleResult",
    "AddCommentToArticleUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import CommentWithExtra, CreateCommentInput
from conduit.core.entities.errors import ArticleDoesNotExistError, UserIsNotAuthenticatedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_article, is_user_followed

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddCommentToArticleInput(WithAuthenticationInput):
    article_slug: ArticleSlug
    body: str

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class AddCommentToArticleResult:
    comment: CommentWithExtra


class AddCommentToArticleUseCase(UseCase[AddCommentToArticleInput, AddCommentToArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: AddCommentToArticleInput, /) -> AddCommentToArticleResult:
        """Add a new comment to an article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            ArticleDoesNotExistError: If article does not exist.
        """
        user_id = input.ensure_authenticated()
        author = await self._get_author(user_id)
        is_author_followed = await is_user_followed(self._unit_of_work, author.id, by=author.id)
        article = await get_article(self._unit_of_work, input.article_slug)
        if article is None:
            raise ArticleDoesNotExistError()
        async with self._unit_of_work.begin() as uow:
            comment = await uow.comments.create(CreateCommentInput(user_id, article.id, input.body))
        LOG.info(
            "comment has been created",
            extra={"comment_id": comment.id, "article_id": article.id, "user_id": user_id},
        )
        return AddCommentToArticleResult(CommentWithExtra(comment, author, is_author_followed))

    async def _get_author(self, user_id: UserId) -> User:
        async with self._unit_of_work.begin() as uow:
            author = await uow.users.get_by_id(user_id)
        if author is None:
            LOG.info("could not find user by id", extra={"user_id": user_id})
            raise UserIsNotAuthenticatedError()
        return author
