import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.get import GetArticleInput, GetArticleUseCase
from tests.unit.conftest import FakeArticleRepository


@pytest.fixture
def use_case(article_repository: FakeArticleRepository) -> GetArticleUseCase:
    return GetArticleUseCase(article_repository)


async def test_get_article_success(
    use_case: GetArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    input = GetArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-get-article-slug-1"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article == existing_article
    assert article_repository.get_by_slug_slug == ArticleSlug("test-get-article-slug-1")
    assert article_repository.get_by_slug_by == existing_user.id


async def test_get_article_success_not_authenticated(
    use_case: GetArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_article: Article,
) -> None:
    # Act
    input = GetArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-get-article-slug-2"),
    )
    result = await use_case.execute(input)

    # Assert
    assert result.article == existing_article
    assert article_repository.get_by_slug_slug == ArticleSlug("test-get-article-slug-2")
    assert article_repository.get_by_slug_by is None


async def test_get_article_not_found(
    use_case: GetArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = GetArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-get-article-slug-3"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is None
    assert article_repository.get_by_slug_slug == ArticleSlug("test-get-article-slug-3")
    assert article_repository.get_by_slug_by == existing_user.id
