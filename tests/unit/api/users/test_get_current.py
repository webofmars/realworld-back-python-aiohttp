import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.get_current import GetCurrentUserInput, GetCurrentUserResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[GetCurrentUserInput, GetCurrentUserResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    get_current_user = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> GetCurrentUserResult:
    return GetCurrentUserResult(
        user=User(
            id=UserId(1),
            username=Username("test"),
            email=Email("test@test.test"),
            password=PasswordHash("test"),
            bio="",
            image=None,
        ),
        token=AuthToken("test"),
    )


@pytest.fixture
def use_case(use_case_result: GetCurrentUserResult) -> UseCase[GetCurrentUserInput, GetCurrentUserResult]:
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
            GetCurrentUserInput(token=AuthToken("test-auth-token"), user_id=None),
            200,
        ),
        pytest.param(
            {"authorization": "Token test-auth-token-2"},
            GetCurrentUserInput(token=AuthToken("test-auth-token-2"), user_id=None),
            200,
        ),
        pytest.param(
            {},
            None,
            422,
        ),
        pytest.param(
            {"authorization": "invalid-token"},
            None,
            422,
        ),
    ],
)
async def test_get_current_user_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[GetCurrentUserInput, GetCurrentUserResult],
    request_headers: dict[str, str],
    expected_input: GetCurrentUserInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.get("/api/v1/user", headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            GetCurrentUserResult(
                user=User(
                    id=UserId(1),
                    username=Username("test"),
                    email=Email("test@test.test"),
                    password=PasswordHash("test"),
                    bio="",
                    image=None,
                ),
                token=AuthToken("test-token"),
            ),
            {
                "user": {
                    "username": "test",
                    "email": "test@test.test",
                    "token": "test-token",
                    "bio": "",
                    "image": None,
                }
            },
        ),
        pytest.param(
            GetCurrentUserResult(
                user=User(
                    id=UserId(1),
                    username=Username("test-2"),
                    email=Email("test-2@test.test"),
                    password=PasswordHash("test-2"),
                    bio="test bio",
                    image=URL("https://test.test/image.jpg"),
                ),
                token=AuthToken("test-token-2"),
            ),
            {
                "user": {
                    "username": "test-2",
                    "email": "test-2@test.test",
                    "token": "test-token-2",
                    "bio": "test bio",
                    "image": "https://test.test/image.jpg",
                }
            },
        ),
    ],
)
async def test_get_current_user_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[GetCurrentUserInput, GetCurrentUserResult],
    use_case_result: GetCurrentUserResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/user", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
