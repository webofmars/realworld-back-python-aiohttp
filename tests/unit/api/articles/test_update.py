import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.update import UpdateArticleInput, UpdateArticleResult
from tests.unit.api.articles.conftest import (
    ARTICLE_1,
    ARTICLE_2,
    EXPECTED_SERIALIZED_ARTICLE_1,
    EXPECTED_SERIALIZED_ARTICLE_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[UpdateArticleInput, UpdateArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    update_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> UpdateArticleResult:
    return UpdateArticleResult(ARTICLE_1)


@pytest.fixture
def use_case(use_case_result: UpdateArticleResult) -> UseCase[UpdateArticleInput, UpdateArticleResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.fixture
def request_body() -> object:
    return {"article": {"title": "new-title", "description": "new-description", "body": "new-body"}}


@pytest.mark.parametrize(
    ["url_path", "request_headers", "request_body", "expected_input", "expected_status"],
    [
        pytest.param(
            "/api/v1/articles/test-1",
            {"authorization": "Token test-auth-token"},
            {"article": {}},
            UpdateArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                slug=ArticleSlug("test-1"),
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2",
            {"authorization": "Token token"},
            {"article": {"title": "new-title"}},
            UpdateArticleInput(
                token=AuthToken("token"),
                user_id=None,
                slug=ArticleSlug("test-2"),
                title="new-title",
            ),
            200,
            id="2",
        ),
        pytest.param(
            "/api/v1/articles/test-3",
            {"authorization": "Token token"},
            {"article": {"title": "new-title", "description": "new-description", "body": "new-body"}},
            UpdateArticleInput(
                token=AuthToken("token"),
                user_id=None,
                slug=ArticleSlug("test-3"),
                title="new-title",
                description="new-description",
                body="new-body",
            ),
            200,
            id="3",
        ),
        pytest.param(
            "/api/v1/articles/test-2",
            {},
            {"article": {"title": "new-title", "description": "new-description", "body": "new-body"}},
            None,
            422,
            id="4",
        ),
        pytest.param(
            "/api/v1/articles/test-2",
            {"authorization": "Token token"},
            {"articles": {}},
            None,
            422,
            id="5",
        ),
    ],
)
async def test_update_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[UpdateArticleInput, UpdateArticleResult],
    url_path: str,
    request_headers: dict[str, str],
    request_body: object,
    expected_input: UpdateArticleInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.put(url_path, headers=request_headers, json=request_body)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body, expected_status",
    [
        pytest.param(
            UpdateArticleResult(ARTICLE_1),
            {"article": EXPECTED_SERIALIZED_ARTICLE_1},
            200,
            id="1",
        ),
        pytest.param(
            UpdateArticleResult(ARTICLE_2),
            {"article": EXPECTED_SERIALIZED_ARTICLE_2},
            200,
            id="2",
        ),
        pytest.param(
            UpdateArticleResult(None),
            {"error": "article not found"},
            404,
            id="3",
        ),
    ],
)
async def test_update_article_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[UpdateArticleInput, UpdateArticleResult],
    use_case_result: UpdateArticleResult,
    request_headers: dict[str, str],
    request_body: object,
    expected_response_body: object,
    expected_status: int,
) -> None:
    # Act
    resp = await client.put("/api/v1/articles/test", headers=request_headers, json=request_body)

    # Assert
    assert await resp.json() == expected_response_body
    assert resp.status == expected_status
