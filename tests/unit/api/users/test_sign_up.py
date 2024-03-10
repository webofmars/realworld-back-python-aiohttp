import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, RawPassword, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.sign_up import SignUpInput, SignUpResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[SignUpInput, SignUpResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    sign_up = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> SignUpResult:
    return SignUpResult(
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
def use_case(use_case_result: SignUpResult) -> UseCase[SignUpInput, SignUpResult]:
    USE_CASE.input = None
    USE_CASE.result = use_case_result
    return USE_CASE


@pytest.fixture
def request_body() -> object:
    return {"user": {"username": "foo", "email": "test@test.test", "password": "test_password"}}


@pytest.mark.parametrize(
    ["request_body", "expected_input", "expected_status"],
    [
        pytest.param(
            {"user": {"username": "foo", "email": "test@test.test", "password": "test_password"}},
            SignUpInput(
                username=Username("foo"),
                email=Email("test@test.test"),
                raw_password=RawPassword("test_password"),
            ),
            201,
        ),
        pytest.param(
            {"user": {"username": "bar", "email": "test-2@test.test", "password": "12345678"}},
            SignUpInput(
                username=Username("bar"),
                email=Email("test-2@test.test"),
                raw_password=RawPassword("12345678"),
            ),
            201,
        ),
        pytest.param(
            {"user": {}},
            None,
            422,
        ),
    ],
)
async def test_sign_up_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[SignUpInput, SignUpResult],
    request_body: object,
    expected_input: SignUpInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.post("/api/v1/users", json=request_body)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            SignUpResult(
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
            SignUpResult(
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
async def test_sign_up_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[SignUpInput, SignUpResult],
    use_case_result: SignUpResult,
    request_body: object,
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.post("/api/v1/users", json=request_body)

    # Assert
    assert await resp.json() == expected_response_body
