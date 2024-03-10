import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, RawPassword, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.update_current import UpdateCurrentUserInput, UpdateCurrentUserResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[UpdateCurrentUserInput, UpdateCurrentUserResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    update_current_user = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> UpdateCurrentUserResult:
    return UpdateCurrentUserResult(
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
def use_case(use_case_result: UpdateCurrentUserResult) -> UseCase[UpdateCurrentUserInput, UpdateCurrentUserResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_body() -> object:
    return {"user": {"username": "foo", "email": "test@test.test", "password": "test_password"}}


@pytest.fixture
def request_headers() -> dict[str, str]:
    return {"authorization": "Token test-auth-token"}


@pytest.mark.parametrize(
    ["request_body", "request_headers", "expected_input", "expected_status"],
    [
        pytest.param(
            {"user": {}},
            {"authorization": "Token test-auth-token"},
            UpdateCurrentUserInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
            ),
            200,
            id="1",
        ),
        pytest.param(
            {"user": {"username": "foo", "email": "test@test.test", "password": "test_password"}},
            {"authorization": "Token test-auth-token"},
            UpdateCurrentUserInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                username=Username("foo"),
                email=Email("test@test.test"),
                password=RawPassword("test_password"),
            ),
            200,
            id="2",
        ),
        pytest.param(
            {
                "user": {
                    "username": "bar",
                    "email": "test@test.test",
                    "password": "new-password",
                    "bio": "new bio",
                    "image": "https://test.test/image.jpg",
                },
            },
            {"authorization": "Token test-auth-token-2"},
            UpdateCurrentUserInput(
                token=AuthToken("test-auth-token-2"),
                user_id=None,
                username=Username("bar"),
                email=Email("test@test.test"),
                password=RawPassword("new-password"),
                bio="new bio",
                image=URL("https://test.test/image.jpg"),
            ),
            200,
            id="3",
        ),
        pytest.param(
            {"user": {"image": None}},
            {"authorization": "Token test-auth-token-3"},
            UpdateCurrentUserInput(
                token=AuthToken("test-auth-token-3"),
                user_id=None,
                image=None,
            ),
            200,
            id="4",
        ),
        pytest.param(
            {"user": None},
            {"authorization": "Token test-auth-token-3"},
            None,
            422,
            id="5",
        ),
    ],
)
async def test_update_current_user_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[UpdateCurrentUserInput, UpdateCurrentUserResult],
    request_body: object,
    request_headers: dict[str, str],
    expected_input: UpdateCurrentUserInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.put("/api/v1/user", json=request_body, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            UpdateCurrentUserResult(
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
            UpdateCurrentUserResult(
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
async def test_update_current_user_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[UpdateCurrentUserInput, UpdateCurrentUserResult],
    use_case_result: UpdateCurrentUserResult,
    request_body: object,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.put("/api/v1/user", json=request_body, headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
