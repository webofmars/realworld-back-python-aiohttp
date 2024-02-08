import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.unfavorite import UnfavoriteArticleInput, UnfavoriteArticleUseCase
from tests.unit.conftest import FakeArticleRepository


@pytest.fixture
def use_case(article_repository: FakeArticleRepository) -> UnfavoriteArticleUseCase:
    return UnfavoriteArticleUseCase(article_repository)


async def test_unfavorite_article_success(
    use_case: UnfavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    input = UnfavoriteArticleInput(token=AuthToken(""), user_id=None, slug=ArticleSlug("test-article-slug-1"))
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article == existing_article
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-1")
    assert article_repository.update_input is not None
    assert article_repository.update_input.title is NotSet.NOT_SET
    assert article_repository.update_input.description is NotSet.NOT_SET
    assert article_repository.update_input.body is NotSet.NOT_SET
    assert article_repository.update_input.is_favorite is False
    assert article_repository.update_id == existing_article.id
    assert article_repository.update_by == existing_user.id


async def test_unfavorite_article_not_authenticated(
    use_case: UnfavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = UnfavoriteArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-1"),
        )
        await use_case.execute(input)

    # Assert
    assert article_repository.update_id is None


async def test_unfavorite_article_not_found(
    use_case: UnfavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = UnfavoriteArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-article-slug-2"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is None
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-2")
    assert article_repository.update_id is None
