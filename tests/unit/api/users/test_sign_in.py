import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, RawPassword, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.sign_in import SignInInput, SignInResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[SignInInput, SignInResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    sign_in = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> SignInResult:
    return SignInResult(
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
def use_case(use_case_result: SignInResult) -> UseCase[SignInInput, SignInResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_body() -> object:
    return {"user": {"email": "test@test.test", "password": "test_password"}}


@pytest.mark.parametrize(
    ["request_body", "expected_input", "expected_status"],
    [
        pytest.param(
            {"user": {"email": "test@test.test", "password": "test_password"}},
            SignInInput(
                email=Email("test@test.test"),
                password=RawPassword("test_password"),
            ),
            200,
        ),
        pytest.param(
            {"user": {"email": "test-2@test.test", "password": "12345678"}},
            SignInInput(
                email=Email("test-2@test.test"),
                password=RawPassword("12345678"),
            ),
            200,
        ),
        pytest.param(
            {"user": {"email": "", "password": "12345678"}},
            None,
            422,
        ),
        pytest.param(
            {"user": {"email": "test@test.test"}},
            None,
            422,
        ),
    ],
)
async def test_sign_in_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[SignInInput, SignInResult],
    request_body: object,
    expected_input: SignInInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.post("/api/v1/users/login", json=request_body)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            SignInResult(
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
            SignInResult(
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
async def test_sign_in_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[SignInInput, SignInResult],
    use_case_result: SignInResult,
    request_body: object,
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.post("/api/v1/users/login", json=request_body)

    # Assert
    assert await resp.json() == expected_response_body
