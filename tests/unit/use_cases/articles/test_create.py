import pytest

from conduit.core.entities.article import Article, Tag
from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.create import CreateArticleInput, CreateArticleUseCase
from tests.unit.conftest import FakeArticleRepository, FakeTagRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> CreateArticleUseCase:
    return CreateArticleUseCase(unit_of_work)


async def test_create_article_success(
    use_case: CreateArticleUseCase,
    article_repository: FakeArticleRepository,
    tag_repository: FakeTagRepository,
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
        tags=[Tag("test"), Tag("foo")],
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.article.v == existing_article
    assert result.article.author == existing_user
    assert article_repository.create_input is not None
    assert article_repository.create_input.title == "test-title-1"
    assert article_repository.create_input.description == "test-description-1"
    assert article_repository.create_input.body == "test-body-1"
    assert tag_repository.tags[existing_article.id] == [Tag("test"), Tag("foo")]


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
