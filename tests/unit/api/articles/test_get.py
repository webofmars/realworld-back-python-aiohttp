import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.get import GetArticleInput, GetArticleResult
from tests.unit.api.articles.conftest import (
    ARTICLE_1,
    ARTICLE_2,
    EXPECTED_SERIALIZED_ARTICLE_1,
    EXPECTED_SERIALIZED_ARTICLE_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[GetArticleInput, GetArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    get_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> GetArticleResult:
    return GetArticleResult(ARTICLE_1)


@pytest.fixture
def use_case(use_case_result: GetArticleResult) -> UseCase[GetArticleInput, GetArticleResult]:
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
            "/api/v1/articles/test-1",
            {"authorization": "Token test-auth-token"},
            GetArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                slug=ArticleSlug("test-1"),
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2",
            {},
            GetArticleInput(
                token=None,
                user_id=None,
                slug=ArticleSlug("test-2"),
            ),
            200,
            id="2",
        ),
    ],
)
async def test_get_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[GetArticleInput, GetArticleResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: GetArticleInput | None,
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
            GetArticleResult(ARTICLE_1),
            {"article": EXPECTED_SERIALIZED_ARTICLE_1},
            id="1",
        ),
        pytest.param(
            GetArticleResult(ARTICLE_2),
            {"article": EXPECTED_SERIALIZED_ARTICLE_2},
            id="2",
        ),
        pytest.param(
            GetArticleResult(None),
            {"error": "article not found"},
            id="3",
        ),
    ],
)
async def test_get_article_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[GetArticleInput, GetArticleResult],
    use_case_result: GetArticleResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/articles/test", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
