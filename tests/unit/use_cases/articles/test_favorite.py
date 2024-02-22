import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.favorite import FavoriteArticleInput, FavoriteArticleUseCase
from tests.unit.conftest import FakeArticleRepository, FakeFavoriteRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> FavoriteArticleUseCase:
    return FavoriteArticleUseCase(unit_of_work)


async def test_favorite_article_success(
    use_case: FavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
    favorite_repository: FakeFavoriteRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    input = FavoriteArticleInput(token=AuthToken(""), user_id=None, slug=ArticleSlug("test-article-slug-1"))
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is not None
    assert result.article.v == existing_article
    assert result.article.is_article_favorite
    assert await favorite_repository.is_favorite(existing_article.id, of=existing_user.id)


async def test_favorite_article_not_authenticated(
    use_case: FavoriteArticleUseCase,
    favorite_repository: FakeFavoriteRepository,
    existing_article: Article,
    existing_user: User,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = FavoriteArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-1"),
        )
        await use_case.execute(input)

    # Assert
    assert not await favorite_repository.is_favorite(existing_article.id, of=existing_user.id)


async def test_favorite_article_not_found(
    use_case: FavoriteArticleUseCase,
    article_repository: FakeArticleRepository,
    favorite_repository: FakeFavoriteRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = FavoriteArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-article-slug-2"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is None
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-2")
    assert not await favorite_repository.is_favorite(existing_article.id, of=existing_user.id)
