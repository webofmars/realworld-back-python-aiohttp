import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.unfavorite import UnfavoriteArticleInput, UnfavoriteArticleUseCase
from tests.unit.conftest import FakeArticleRepository, FakeFavoriteRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> UnfavoriteArticleUseCase:
    return UnfavoriteArticleUseCase(unit_of_work)


async def test_unfavorite_article_success(
    use_case: UnfavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
    favorite_repository: FakeFavoriteRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    favorite_repository.favorites[existing_article.id] = {existing_user.id}

    # Act
    input = UnfavoriteArticleInput(token=AuthToken(""), user_id=None, slug=ArticleSlug("test-article-slug-1"))
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is not None
    assert result.article.v == existing_article
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-1")
    assert not await favorite_repository.is_favorite(existing_article.id, of=existing_user.id)


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
    assert article_repository.get_by_slug_slug is None


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
