import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import ArticleId, ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.delete import DeleteArticleInput, DeleteArticleResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[DeleteArticleInput, DeleteArticleResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    delete_article = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> DeleteArticleResult:
    return DeleteArticleResult(ArticleId(123))


@pytest.fixture
def use_case(use_case_result: DeleteArticleResult) -> UseCase[DeleteArticleInput, DeleteArticleResult]:
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
            DeleteArticleInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                slug=ArticleSlug("test-1"),
            ),
            204,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-2",
            {"authorization": "Token token"},
            DeleteArticleInput(
                token=AuthToken("token"),
                user_id=None,
                slug=ArticleSlug("test-2"),
            ),
            204,
            id="1",
        ),
        pytest.param(
            "/api/v1/articles/test-3",
            {},
            None,
            422,
            id="3",
        ),
    ],
)
async def test_delete_article_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[DeleteArticleInput, DeleteArticleResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: DeleteArticleInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.delete(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input
