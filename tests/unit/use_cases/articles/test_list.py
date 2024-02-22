import pytest

from conduit.core.entities.article import ArticleFilter, Tag
from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.articles.list import ListArticlesInput, ListArticlesUseCase
from tests.unit.conftest import FakeArticleRepository, FakeUnitOfWork


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> ListArticlesUseCase:
    return ListArticlesUseCase(unit_of_work)


@pytest.mark.parametrize(
    "input, expected_filter, expected_limit, expected_offset",
    [
        pytest.param(
            ListArticlesInput(
                token=AuthToken(""),
                user_id=None,
                tag=Tag("test-list-articles-tag-1"),
            ),
            ArticleFilter(tag=Tag("test-list-articles-tag-1")),
            20,
            0,
            id="test-1",
        ),
        pytest.param(
            ListArticlesInput(
                token=AuthToken(""),
                user_id=None,
                author=Username("test-list-articles-author-1"),
                limit=19,
                offset=1,
            ),
            ArticleFilter(author=Username("test-list-articles-author-1")),
            19,
            1,
            id="test-2",
        ),
        pytest.param(
            ListArticlesInput(
                token=AuthToken(""),
                user_id=None,
                favorite_of=Username("test-list-articles-author-2"),
                limit=10,
                offset=10,
            ),
            ArticleFilter(favorite_of=Username("test-list-articles-author-2")),
            10,
            10,
            id="test-3",
        ),
    ],
)
async def test_list_articles_success(
    use_case: ListArticlesUseCase,
    article_repository: FakeArticleRepository,
    existing_user: User,
    input: ListArticlesInput,
    expected_filter: ArticleFilter,
    expected_limit: int,
    expected_offset: int,
) -> None:
    # Act
    await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert article_repository.get_many_filter == expected_filter
    assert article_repository.get_many_limit == expected_limit
    assert article_repository.get_many_offset == expected_offset
    assert article_repository.count_filter == expected_filter


async def test_list_article_success_not_authenticated(
    use_case: ListArticlesUseCase,
    article_repository: FakeArticleRepository,
) -> None:
    # Act
    input = ListArticlesInput(token=AuthToken(""), user_id=None, limit=5, offset=1)
    await use_case.execute(input)

    # Assert
    assert article_repository.get_many_filter is not None
    assert article_repository.get_many_limit == 5
    assert article_repository.get_many_offset == 1
