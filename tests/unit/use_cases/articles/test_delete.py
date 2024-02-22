from dataclasses import replace

import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.errors import PermissionDeniedError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, UserId
from conduit.core.use_cases.articles.delete import DeleteArticleInput, DeleteArticleUseCase
from tests.unit.conftest import FakeArticleRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> DeleteArticleUseCase:
    return DeleteArticleUseCase(unit_of_work)


async def test_delete_article_success(
    use_case: DeleteArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    input = DeleteArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-article-slug-1"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.id == existing_article.id
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-1")
    assert article_repository.delete_id == existing_article.id


async def test_delete_article_not_authenticated(
    use_case: DeleteArticleUseCase,
    article_repository: FakeArticleRepository,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = DeleteArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-1"),
        )
        await use_case.execute(input)

    # Assert
    assert article_repository.delete_id is None


async def test_delete_article_not_found(
    use_case: DeleteArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = DeleteArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-article-slug-2"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.id is None
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-2")
    assert article_repository.delete_id is None


async def test_delete_article_permission_denied(
    use_case: DeleteArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = replace(existing_article, author_id=UserId(123456))

    # Act
    with pytest.raises(PermissionDeniedError):
        input = DeleteArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-3"),
        )
        await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-3")
    assert article_repository.delete_id is None
