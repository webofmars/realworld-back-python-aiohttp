import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.feed import FeedArticlesInput, FeedArticlesResult
from tests.unit.api.articles.conftest import (
    ARTICLE_1,
    ARTICLE_2,
    EXPECTED_SERIALIZED_ARTICLE_1,
    EXPECTED_SERIALIZED_ARTICLE_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[FeedArticlesInput, FeedArticlesResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    feed_articles = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> FeedArticlesResult:
    return FeedArticlesResult(articles=[ARTICLE_1], count=12)


@pytest.fixture
def use_case(use_case_result: FeedArticlesResult) -> UseCase[FeedArticlesInput, FeedArticlesResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.mark.parametrize(
    ["url_path", "request_headers", "expected_input", "expected_status"],
    [
        pytest.param(
            "/api/v1/articles/feed",
            {"authorization": "Token test-auth-token"},
            FeedArticlesInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/feed?limit=41&offset=123",
            {"authorization": "Token token"},
            FeedArticlesInput(
                token=AuthToken("token"),
                user_id=None,
                limit=41,
                offset=123,
            ),
            200,
            id="2",
        ),
        pytest.param(
            "/api/v1/articles/feed",
            {},
            None,
            422,
            id="3",
        ),
    ],
)
async def test_feed_articles_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[FeedArticlesInput, FeedArticlesResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: FeedArticlesInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.get(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            FeedArticlesResult(articles=[], count=0),
            {"articles": [], "articlesCount": 0},
            id="1",
        ),
        pytest.param(
            FeedArticlesResult(articles=[ARTICLE_1], count=123),
            {"articles": [EXPECTED_SERIALIZED_ARTICLE_1], "articlesCount": 123},
            id="2",
        ),
        pytest.param(
            FeedArticlesResult(articles=[ARTICLE_1, ARTICLE_2], count=2),
            {"articles": [EXPECTED_SERIALIZED_ARTICLE_1, EXPECTED_SERIALIZED_ARTICLE_2], "articlesCount": 2},
            id="3",
        ),
    ],
)
async def test_feed_articles_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[FeedArticlesInput, FeedArticlesResult],
    use_case_result: FeedArticlesResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/articles/feed", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
