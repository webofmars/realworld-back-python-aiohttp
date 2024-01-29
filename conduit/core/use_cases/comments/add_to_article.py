__all__ = [
    "AddCommentToArticleInput",
    "AddCommentToArticleResult",
    "AddCommentToArticleUseCase",
]

import logging
from dataclasses import dataclass

from conduit.core.entities.article import ArticleRepository, ArticleSlug
from conduit.core.entities.comment import Comment, CommentRepository, CreateCommentInput
from conduit.core.entities.errors import ArticleDoesNotExistError
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddCommentToArticleInput(WithAuthenticationInput):
    article_slug: ArticleSlug
    body: str


@dataclass(frozen=True)
class AddCommentToArticleResult:
    comment: Comment


class AddCommentToArticleUseCase(UseCase[AddCommentToArticleInput, AddCommentToArticleResult]):
    def __init__(self, article_repository: ArticleRepository, comment_repository: CommentRepository) -> None:
        self._article_repository = article_repository
        self._comment_repository = comment_repository

    async def execute(self, input: AddCommentToArticleInput, /) -> AddCommentToArticleResult:
        """Add a new comment to an article.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            ArticleDoesNotExistError: If article does not exist.
        """
        user_id = input.ensure_authenticated()
        article = await self._article_repository.get_by_slug(input.article_slug, user_id)
        if article is None:
            LOG.info(
                "could not add a new comment, the article is not found",
                extra={"slug": input.article_slug, "user_id": user_id},
            )
            raise ArticleDoesNotExistError()
        comment = await self._comment_repository.create(CreateCommentInput(article.id, input.body), by=user_id)
        LOG.info(
            "comment has been created",
            extra={"comment_id": comment.id, "article_id": article.id, "user_id": user_id},
        )
        return AddCommentToArticleResult(comment)
