import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.comment import Comment
from conduit.core.entities.errors import ArticleDoesNotExistError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.comments.add_to_article import AddCommentToArticleInput, AddCommentToArticleUseCase
from tests.unit.conftest import FakeArticleRepository, FakeCommentRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> AddCommentToArticleUseCase:
    return AddCommentToArticleUseCase(unit_of_work)


async def test_add_comment_to_article_success(
    use_case: AddCommentToArticleUseCase,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Act
    input = AddCommentToArticleInput(
        token=AuthToken(""),
        user_id=None,
        article_slug=existing_article.slug,
        body="test-add-comment-to-article",
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.comment.v == existing_comment
    assert comment_repository.create_input is not None
    assert comment_repository.create_input.article_id == existing_article.id
    assert comment_repository.create_input.body == "test-add-comment-to-article"
    assert comment_repository.create_input.author_id == existing_user.id


async def test_add_comment_to_article_not_authenticated(
    use_case: AddCommentToArticleUseCase,
    comment_repository: FakeCommentRepository,
    existing_article: Article,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = AddCommentToArticleInput(
            token=AuthToken(""),
            user_id=None,
            article_slug=existing_article.slug,
            body="test-add-comment-to-article",
        )
        await use_case.execute(input)

    # Assert
    assert comment_repository.create_input is None


async def test_add_comment_to_article_article_not_found(
    use_case: AddCommentToArticleUseCase,
    article_repository: FakeArticleRepository,
    comment_repository: FakeCommentRepository,
    existing_comment: Comment,
    existing_user: User,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    with pytest.raises(ArticleDoesNotExistError):
        input = AddCommentToArticleInput(
            token=AuthToken(""),
            user_id=None,
            article_slug=ArticleSlug("not-existing-article"),
            body="test-add-comment-to-article",
        )
        await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert comment_repository.create_input is None
    assert article_repository.get_by_slug_slug == ArticleSlug("not-existing-article")
