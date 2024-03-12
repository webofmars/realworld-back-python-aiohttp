import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.get_from_article import GetCommentsFromArticleInput, GetCommentsFromArticleResult
from tests.unit.api.comments.conftest import (
    COMMENT_1,
    COMMENT_2,
    EXPECTED_SERIALIZED_COMMENT_1,
    EXPECTED_SERIALIZED_COMMENT_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    get_comments_from_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> GetCommentsFromArticleResult:
    return GetCommentsFromArticleResult([COMMENT_1])


@pytest.fixture
def use_case(
    use_case_result: GetCommentsFromArticleResult,
) -> UseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult]:
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
            "/api/v1/articles/test-1/comments",
            {"authorization": "Token test-auth-token"},
            GetCommentsFromArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                article_slug=ArticleSlug("test-1"),
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2/comments",
            {},
            GetCommentsFromArticleInput(
                token=None,
                user_id=None,
                article_slug=ArticleSlug("test-2"),
            ),
            200,
            id="2",
        ),
    ],
)
async def test_get_comments_from_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: GetCommentsFromArticleInput | None,
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
            GetCommentsFromArticleResult([]),
            {"comments": []},
            id="1",
        ),
        pytest.param(
            GetCommentsFromArticleResult([COMMENT_1]),
            {"comments": [EXPECTED_SERIALIZED_COMMENT_1]},
            id="2",
        ),
        pytest.param(
            GetCommentsFromArticleResult([COMMENT_1, COMMENT_2]),
            {"comments": [EXPECTED_SERIALIZED_COMMENT_1, EXPECTED_SERIALIZED_COMMENT_2]},
            id="2",
        ),
    ],
)
async def test_get_comments_from_article_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult],
    use_case_result: GetCommentsFromArticleResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/articles/test/comments", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
