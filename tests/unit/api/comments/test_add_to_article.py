import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.add_to_article import AddCommentToArticleInput, AddCommentToArticleResult
from tests.unit.api.comments.conftest import (
    COMMENT_1,
    COMMENT_2,
    EXPECTED_SERIALIZED_COMMENT_1,
    EXPECTED_SERIALIZED_COMMENT_2,
)
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[AddCommentToArticleInput, AddCommentToArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    add_comment_to_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> AddCommentToArticleResult:
    return AddCommentToArticleResult(COMMENT_1)


@pytest.fixture
def use_case(
    use_case_result: AddCommentToArticleResult,
) -> UseCase[AddCommentToArticleInput, AddCommentToArticleResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_body() -> object:
    return {"comment": {"body": "test-comment"}}


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.mark.parametrize(
    ["url_path", "request_body", "request_headers", "expected_input", "expected_status"],
    [
        pytest.param(
            "/api/v1/articles/test-1/comments",
            {"comment": {"body": "test-comment-1"}},
            {"authorization": "Token test-auth-token"},
            AddCommentToArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                article_slug=ArticleSlug("test-1"),
                body="test-comment-1",
            ),
            201,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2/comments",
            {"comment": {"body": "test-comment-2"}},
            {"authorization": "Token token"},
            AddCommentToArticleInput(
                token=AuthToken("token"),
                user_id=None,
                article_slug=ArticleSlug("test-2"),
                body="test-comment-2",
            ),
            201,
            id="2",
        ),
        pytest.param(
            "/api/v1/articles/test-2/comments",
            {"comment": {"body": "test-comment-2"}},
            {},
            None,
            422,
            id="3",
        ),
        pytest.param(
            "/api/v1/articles/test-2/comments",
            {"comment": {}},
            {"authorization": "Token token"},
            None,
            422,
            id="4",
        ),
    ],
)
async def test_add_comment_to_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[AddCommentToArticleInput, AddCommentToArticleResult],
    url_path: str,
    request_body: object,
    request_headers: dict[str, str],
    expected_input: AddCommentToArticleInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.post(url_path, json=request_body, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            AddCommentToArticleResult(COMMENT_1),
            {"comment": EXPECTED_SERIALIZED_COMMENT_1},
            id="1",
        ),
        pytest.param(
            AddCommentToArticleResult(COMMENT_2),
            {"comment": EXPECTED_SERIALIZED_COMMENT_2},
            id="2",
        ),
    ],
)
async def test_add_comment_to_article_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[AddCommentToArticleInput, AddCommentToArticleResult],
    use_case_result: AddCommentToArticleResult,
    request_body: object,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.post("/api/v1/articles/test/comments", json=request_body, headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
