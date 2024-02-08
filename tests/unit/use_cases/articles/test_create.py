import pytest

from conduit.core.entities.article import Article
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.tag import Tag
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.create import CreateArticleInput, CreateArticleUseCase
from tests.unit.conftest import FakeArticleRepository


@pytest.fixture
def use_case(article_repository: FakeArticleRepository) -> CreateArticleUseCase:
    return CreateArticleUseCase(article_repository)


async def test_create_article_success(
    use_case: CreateArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    input = CreateArticleInput(
        token=AuthToken(""),
        user_id=None,
        title="test-title-1",
        description="test-description-1",
        body="test-body-1",
        tags=[Tag("test"), Tag("foo"), Tag("test")],
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article == existing_article
    assert article_repository.create_input is not None
    assert article_repository.create_input.title == "test-title-1"
    assert article_repository.create_input.description == "test-description-1"
    assert article_repository.create_input.body == "test-body-1"
    assert article_repository.create_input.tags == [Tag("test"), Tag("foo")]
    assert article_repository.create_by == existing_user.id


async def test_create_article_not_authenticated(
    use_case: CreateArticleUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    existing_article: Article,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = CreateArticleInput(
            token=AuthToken(""),
            user_id=None,
            title="test-title-1",
            description="test-description-1",
            body="test-body-1",
            tags=[Tag("test"), Tag("foo"), Tag("test")],
        )
        await use_case.execute(input)

    # Assert
    assert article_repository.create_input is None
    assert article_repository.create_by is None
