from dataclasses import replace

import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.comment import Comment, CommentId
from conduit.core.entities.errors import PermissionDeniedError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, UserId
from conduit.core.use_cases.comments.delete import DeleteCommentInput, DeleteCommentUseCase
from tests.unit.conftest import FakeArticleRepository, FakeCommentRepository


@pytest.fixture
def use_case(
    article_repository: FakeArticleRepository,
    comment_repository: FakeCommentRepository,
) -> DeleteCommentUseCase:
    return DeleteCommentUseCase(article_repository, comment_repository)


async def test_delete_comment_success(
    use_case: DeleteCommentUseCase,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Act
    input = DeleteCommentInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=existing_article.slug,
        comment_id=existing_comment.id,
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.comment_id == existing_comment.id
    assert comment_repository.delete_id == existing_comment.id


async def test_delete_comment_not_authenticated(
    use_case: DeleteCommentUseCase,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_comment: Comment,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = DeleteCommentInput(
            token=AuthToken(""),
            user_id=None,
            article_slug=existing_article.slug,
            comment_id=existing_comment.id,
        )
        await use_case.execute(input)

    # Assert
    assert comment_repository.delete_id is None


async def test_delete_comment_article_not_found(
    use_case: DeleteCommentUseCase,
    article_repository: FakeArticleRepository,
    comment_repository: FakeCommentRepository,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = DeleteCommentInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=ArticleSlug("not-existing-article"),
        comment_id=existing_comment.id,
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.comment_id is None
    assert comment_repository.get_by_id_id is None
    assert comment_repository.delete_id is None
    assert article_repository.get_by_slug_slug == ArticleSlug("not-existing-article")


async def test_delete_comment_comment_not_found(
    use_case: DeleteCommentUseCase,
    article_repository: FakeArticleRepository,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_user: User,
) -> None:
    # Arrange
    comment_repository.comment = None

    # Act
    input = DeleteCommentInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=existing_article.slug,
        comment_id=CommentId(123456),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.comment_id is None
    assert comment_repository.get_by_id_id == CommentId(123456)
    assert comment_repository.delete_id is None
    assert article_repository.get_by_slug_slug == existing_article.slug


async def test_delete_comment_permission_denied(
    use_case: DeleteCommentUseCase,
    article_repository: FakeArticleRepository,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Arrange
    assert comment_repository.comment is not None
    comment_repository.comment = replace(
        comment_repository.comment,
        author=replace(comment_repository.comment.author, id=UserId(123456)),
    )

    # Act
    with pytest.raises(PermissionDeniedError):
        input = DeleteCommentInput(
            token=AuthToken(""),
            user_id=None,
            article_slug=existing_article.slug,
            comment_id=existing_comment.id,
        )
        await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert comment_repository.get_by_id_id == existing_comment.id
    assert comment_repository.delete_id is None
    assert article_repository.get_by_slug_slug == existing_article.slug
