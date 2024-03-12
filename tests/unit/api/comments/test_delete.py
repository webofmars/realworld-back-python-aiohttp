import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import CommentId
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.delete import DeleteCommentInput, DeleteCommentResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[DeleteCommentInput, DeleteCommentResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    delete_comment = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> DeleteCommentResult:
    return DeleteCommentResult(CommentId(123))


@pytest.fixture
def use_case(use_case_result: DeleteCommentResult) -> UseCase[DeleteCommentInput, DeleteCommentResult]:
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
            "/api/v1/articles/test-1/comments/1",
            {"authorization": "Token test-auth-token"},
            DeleteCommentInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                article_slug=ArticleSlug("test-1"),
                comment_id=CommentId(1),
            ),
            204,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2/comments/2",
            {"authorization": "Token token"},
            DeleteCommentInput(
                token=AuthToken("token"),
                user_id=None,
                article_slug=ArticleSlug("test-2"),
                comment_id=CommentId(2),
            ),
            204,
            id="2",
        ),
        pytest.param(
            "/api/v1/articles/test-3/comments/3",
            {},
            None,
            422,
            id="3",
        ),
    ],
)
async def test_delete_comment_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[DeleteCommentInput, DeleteCommentResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: DeleteCommentInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.delete(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input
