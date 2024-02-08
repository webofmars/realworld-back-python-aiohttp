from dataclasses import replace

import pytest

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import PermissionDeniedError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, UserId
from conduit.core.use_cases.articles.update import UpdateArticleInput, UpdateArticleUseCase
from tests.unit.conftest import FakeArticleRepository


@pytest.fixture
def use_case(article_repository: FakeArticleRepository) -> UpdateArticleUseCase:
    return UpdateArticleUseCase(article_repository)


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(
            UpdateArticleInput(
                token=AuthToken(""),
                user_id=None,
                slug=ArticleSlug("test-update-article-slug-1"),
            ),
            id="test-1",
        ),
        pytest.param(
            UpdateArticleInput(
                token=AuthToken(""),
                user_id=None,
                slug=ArticleSlug("test-update-article-slug-2"),
                title="test-update-article-title-1",
            ),
            id="test-2",
        ),
        pytest.param(
            UpdateArticleInput(
                token=AuthToken(""),
                user_id=None,
                slug=ArticleSlug("test-update-article-slug-3"),
                title="test-update-article-title-3",
                description="test-update-article-description-3",
                body="test-update-article-body-3",
            ),
            id="test-3",
        ),
    ],
)
async def test_update_article_success(
    use_case: UpdateArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
    input: UpdateArticleInput,
) -> None:
    # Act
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article == existing_article
    assert article_repository.get_by_slug_slug == input.slug
    assert article_repository.update_id == existing_article.id
    assert article_repository.update_input is not None
    assert article_repository.update_input.title == input.title
    assert article_repository.update_input.description == input.description
    assert article_repository.update_input.body == input.body
    assert article_repository.update_input.is_favorite is NotSet.NOT_SET


async def test_update_article_not_authenticated(
    use_case: UpdateArticleUseCase,
    article_repository: FakeArticleRepository,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = UpdateArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-1"),
        )
        await use_case.execute(input)

    # Assert
    assert article_repository.update_id is None


async def test_update_article_not_found(
    use_case: UpdateArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = None

    # Act
    input = UpdateArticleInput(
        token=AuthToken(""),
        user_id=None,
        slug=ArticleSlug("test-article-slug-2"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article is None
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-2")
    assert article_repository.update_id is None


async def test_update_article_permission_denied(
    use_case: UpdateArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Arrange
    article_repository.article = replace(existing_article, author=replace(existing_article.author, id=UserId(123456)))

    # Act
    with pytest.raises(PermissionDeniedError):
        input = UpdateArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug("test-article-slug-3"),
        )
        await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert article_repository.get_by_slug_slug == ArticleSlug("test-article-slug-3")
    assert article_repository.update_id is None
