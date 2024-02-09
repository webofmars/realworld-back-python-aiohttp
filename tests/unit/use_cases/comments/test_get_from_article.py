import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.comment import Comment
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.comments.get_from_article import GetCommentsFromArticleInput, GetCommentsFromArticleUseCase
from tests.unit.conftest import FakeCommentRepository


@pytest.fixture
def use_case(comment_repository: FakeCommentRepository) -> GetCommentsFromArticleUseCase:
    return GetCommentsFromArticleUseCase(comment_repository)


async def test_get_comment_from_article_success(
    use_case: GetCommentsFromArticleUseCase,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Act
    input = GetCommentsFromArticleInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=existing_article.slug,
    )
    await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert comment_repository.get_many_filter is not None
    assert comment_repository.get_many_filter.article_slug == existing_article.slug
    assert comment_repository.get_many_by == existing_user.id


async def test_get_comment_from_article_not_authenticated(
    use_case: GetCommentsFromArticleUseCase,
    comment_repository: FakeCommentRepository,
) -> None:
    # Act
    input = GetCommentsFromArticleInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=ArticleSlug("test-get-comment-from-article"),
    )
    await use_case.execute(input)

    # Assert
    assert comment_repository.get_many_filter is not None
    assert comment_repository.get_many_filter.article_slug == ArticleSlug("test-get-comment-from-article")
    assert comment_repository.get_many_by is None
