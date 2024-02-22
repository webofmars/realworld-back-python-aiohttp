__all__ = [
    "DeleteCommentInput",
    "DeleteCommentResult",
    "DeleteCommentUseCase",
]

import logging
import typing as t
from dataclasses import dataclass, replace

from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import CommentId
from conduit.core.entities.errors import PermissionDeniedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput
from conduit.core.use_cases.common import get_article

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCommentInput(WithAuthenticationInput):
    article_slug: ArticleSlug
    comment_id: CommentId

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class DeleteCommentResult:
    comment_id: CommentId | None


class DeleteCommentUseCase(UseCase[DeleteCommentInput, DeleteCommentResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: DeleteCommentInput, /) -> DeleteCommentResult:
        """Delete an existing comment.

        Raise:
            UserIsNotAuthenticatedError: If user is not authenticated.
            PermissionDeniedError: If user is not allowed to delete the comment.
        """
        user_id = input.ensure_authenticated()
        article = await get_article(self._unit_of_work, input.article_slug)
        if article is None:
            return DeleteCommentResult(None)
        async with self._unit_of_work.begin() as uow:
            comment = await uow.comments.get_by_id(input.comment_id)
        if comment is None:
            LOG.info("could not delete comment, comment not found", extra={"input": input})
            return DeleteCommentResult(None)
        if comment.author_id != user_id:
            LOG.info("user is not allowed to delete the comment", extra={"input": input})
            raise PermissionDeniedError()
        async with self._unit_of_work.begin() as uow:
            comment_id = await uow.comments.delete(comment.id)
        LOG.info("comment has been deleted", extra={"input": input})
        return DeleteCommentResult(comment_id)
