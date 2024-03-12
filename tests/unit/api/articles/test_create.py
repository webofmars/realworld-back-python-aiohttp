import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import Tag
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.create import CreateArticleInput, CreateArticleResult
from tests.unit.api.articles.conftest import (
    ARTICLE_1,
    ARTICLE_2,
    EXPECTED_SERIALIZED_ARTICLE_1,
    EXPECTED_SERIALIZED_ARTICLE_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[CreateArticleInput, CreateArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    create_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> CreateArticleResult:
    return CreateArticleResult(ARTICLE_1)


@pytest.fixture
def use_case(use_case_result: CreateArticleResult) -> UseCase[CreateArticleInput, CreateArticleResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_body() -> object:
    return {
        "article": {
            "title": "test-title",
            "description": "test-description",
            "body": "test-body",
            "tagList": ["test-tag-1", "test-tag-2"],
        }
    }


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.mark.parametrize(
    ["request_body", "request_headers", "expected_input", "expected_status"],
    [
        pytest.param(
            {
                "article": {
                    "title": "test-title",
                    "description": "test-description",
                    "body": "test-body",
                    "tagList": ["test-tag-1", "test-tag-2"],
                }
            },
            {"authorization": "Token test-auth-token"},
            CreateArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                title="test-title",
                description="test-description",
                body="test-body",
                tags=[Tag("test-tag-1"), Tag("test-tag-2")],
            ),
            201,
            id="1",
        ),
        pytest.param(
            {
                "article": {
                    "title": "test-title-2",
                    "description": "",
                    "body": "test-body-2",
                }
            },
            {"authorization": "Token token"},
            CreateArticleInput(
                token=AuthToken("token"),
                user_id=None,
                title="test-title-2",
                description="",
                body="test-body-2",
                tags=[],
            ),
            201,
            id="2",
        ),
        pytest.param(
            {
                "article": {
                    "title": "test-title-2",
                    "description": "",
                    "body": "test-body-2",
                }
            },
            {},
            None,
            422,
            id="3",
        ),
        pytest.param(
            {"article": {}},
            {"authorization": "Token token"},
            None,
            422,
            id="4",
        ),
    ],
)
async def test_create_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[CreateArticleInput, CreateArticleResult],
    request_body: object,
    request_headers: dict[str, str],
    expected_input: CreateArticleInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.post("/api/v1/articles", json=request_body, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            CreateArticleResult(article=ARTICLE_1),
            {"article": EXPECTED_SERIALIZED_ARTICLE_1},
            id="1",
        ),
        pytest.param(
            CreateArticleResult(article=ARTICLE_2),
            {"article": EXPECTED_SERIALIZED_ARTICLE_2},
            id="2",
        ),
    ],
)
async def test_create_article_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[CreateArticleInput, CreateArticleResult],
    use_case_result: CreateArticleResult,
    request_body: object,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.post("/api/v1/articles", json=request_body, headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
