__all__ = [
    "GetCommentsFromArticleInput",
    "GetCommentsFromArticleResult",
    "GetCommentsFromArticleUseCase",
]

import typing as t
from dataclasses import dataclass, replace

import structlog

from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import Comment, CommentFilter, CommentWithExtra
from conduit.core.entities.errors import ArticleDoesNotExistError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithOptionalAuthenticationInput
from conduit.core.use_cases.common import are_users_followed, get_article, get_users

LOG = structlog.get_logger(__name__)


@dataclass(frozen=True)
class GetCommentsFromArticleInput(WithOptionalAuthenticationInput):
    article_slug: ArticleSlug

    def with_user_id(self, id: UserId) -> t.Self:
        return replace(self, user_id=id)


@dataclass(frozen=True)
class GetCommentsFromArticleResult:
    comments: t.List[CommentWithExtra]


class GetCommentsFromArticleUseCase(UseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: GetCommentsFromArticleInput, /) -> GetCommentsFromArticleResult:
        """Get article's comments.

        Raises:
            ArticleDoesNotExistError: If article does not exist.
        """
        user_id = input.user_id
        article = await get_article(self._unit_of_work, input.article_slug)
        if article is None:
            raise ArticleDoesNotExistError()
        async with self._unit_of_work.begin() as uow:
            comments = await uow.comments.get_many(CommentFilter(article.id))
        LOG.info("got comments from the article", input=input)
        author_ids = {comment.author_id for comment in comments}
        authors = await get_users(self._unit_of_work, author_ids)
        followed = await are_users_followed(self._unit_of_work, author_ids, by=user_id)
        return GetCommentsFromArticleResult(self._prepare_comments(comments, authors, followed))

    def _prepare_comments(
        self,
        comments: t.Sequence[Comment],
        authors: t.Mapping[UserId, User],
        followed: t.Mapping[UserId, bool],
    ) -> list[CommentWithExtra]:
        result = []
        for comment in comments:
            author = authors.get(comment.author_id)
            if author is None:
                LOG.error("author of a comment not found", comment_id=comment.id, author_id=comment.author_id)
                continue
            result.append(
                CommentWithExtra(
                    v=comment,
                    author=author,
                    is_author_followed=followed.get(comment.author_id, False),
                )
            )
        return result
