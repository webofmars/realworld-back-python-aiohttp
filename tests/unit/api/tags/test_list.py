import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers

from conduit.container import UseCases
from conduit.core.entities.article import Tag
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.tags.list import ListTagsInput, ListTagsResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[ListTagsInput, ListTagsResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    list_tags = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> ListTagsResult:
    return ListTagsResult([Tag("test-1")])


@pytest.fixture
def use_case(
    use_case_result: ListTagsResult,
) -> UseCase[ListTagsInput, ListTagsResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.mark.parametrize(
    ["request_headers", "expected_input", "expected_status"],
    [
        pytest.param(
            {"authorization": "Token test-auth-token"},
            ListTagsInput(),
            200,
            id="1",
        ),
        pytest.param(
            {},
            ListTagsInput(),
            200,
            id="2",
        ),
    ],
)
async def test_list_tags_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[ListTagsInput, ListTagsResult],
    request_headers: dict[str, str],
    expected_input: ListTagsInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.get("/api/v1/tags", headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            ListTagsResult([]),
            {"tags": []},
            id="1",
        ),
        pytest.param(
            ListTagsResult([Tag("test-1")]),
            {"tags": ["test-1"]},
            id="2",
        ),
        pytest.param(
            ListTagsResult([Tag("test-1"), Tag("test-2")]),
            {"tags": ["test-1", "test-2"]},
            id="3",
        ),
    ],
)
async def test_list_tags_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[ListTagsInput, ListTagsResult],
    use_case_result: ListTagsResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/tags", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
