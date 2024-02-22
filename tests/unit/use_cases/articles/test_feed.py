import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.articles.feed import FeedArticlesInput, FeedArticlesUseCase
from tests.unit.conftest import FakeArticleRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> FeedArticlesUseCase:
    return FeedArticlesUseCase(unit_of_work)


async def test_feed_articles_success(
    use_case: FeedArticlesUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
) -> None:
    # Act
    input = FeedArticlesInput(
        token=AuthToken(""),
        user_id=None,
        limit=19,
        offset=1,
    )
    await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert article_repository.get_many_filter is not None
    assert article_repository.get_many_filter.feed_of == existing_user.id
    assert article_repository.get_many_limit == 19
    assert article_repository.get_many_offset == 1


async def test_feed_articles_not_authenticated(
    use_case: FeedArticlesUseCase,
    article_repository: FakeArticleRepository,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        input = FeedArticlesInput(
            token=AuthToken(""),
            user_id=None,
        )
        await use_case.execute(input)

    # Assert
    assert article_repository.get_many_filter is None
