__all__ = [
    "DeleteCommentInput",
    "DeleteCommentResult",
    "DeleteCommentUseCase",
]

import logging
from dataclasses import dataclass

from conduit.core.entities.article import ArticleRepository, ArticleSlug
from conduit.core.entities.comment import CommentId, CommentRepository
from conduit.core.entities.errors import PermissionDeniedError
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCommentInput(WithAuthenticationInput):
    article_slug: ArticleSlug
    comment_id: CommentId


@dataclass(frozen=True)
class DeleteCommentResult:
    comment_id: CommentId | None


class DeleteCommentUseCase(UseCase[DeleteCommentInput, DeleteCommentResult]):
    def __init__(self, article_repository: ArticleRepository, comment_repository: CommentRepository) -> None:
        self._article_repository = article_repository
        self._comment_repository = comment_repository

    async def execute(self, input: DeleteCommentInput, /) -> DeleteCommentResult:
        """Delete an existing comment.

        Raise:
            UserIsNotAuthenticatedError: If user is not authenticated.
            PermissionDeniedError: If user is not allowed to delete the comment.
        """
        user_id = input.ensure_authenticated()
        article = await self._article_repository.get_by_slug(input.article_slug)
        if article is None:
            LOG.info("could not delete comment, article not found", extra={"input": input})
            return DeleteCommentResult(None)
        comment = await self._comment_repository.get_by_id(input.comment_id)
        if comment is None:
            LOG.info("could not delete comment, comment not found", extra={"input": input})
            return DeleteCommentResult(None)
        if comment.author.user_id != user_id:
            LOG.info("user is not allowed to delete the comment", extra={"input": input})
            raise PermissionDeniedError()
        comment_id = await self._comment_repository.delete(comment.id)
        LOG.info("comment has been deleted", extra={"input": input})
        return DeleteCommentResult(comment_id)
