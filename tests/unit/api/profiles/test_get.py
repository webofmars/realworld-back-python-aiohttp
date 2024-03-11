import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[GetProfileInput, GetProfileResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    get_profile = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> GetProfileResult:
    return GetProfileResult(
        user=User(
            id=UserId(1),
            username=Username("test"),
            email=Email("test@test.test"),
            password=PasswordHash("test"),
            bio="",
            image=None,
        ),
        is_followed=True,
    )


@pytest.fixture
def use_case(use_case_result: GetProfileResult) -> UseCase[GetProfileInput, GetProfileResult]:
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
            "/api/v1/profiles/test",
            {"authorization": "Token test-auth-token"},
            GetProfileInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                username=Username("test"),
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/profiles/test-test-test",
            {},
            GetProfileInput(
                token=None,
                user_id=None,
                username=Username("test-test-test"),
            ),
            200,
            id="2",
        ),
    ],
)
async def test_get_profile_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[GetProfileInput, GetProfileResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: GetProfileInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.get(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            GetProfileResult(
                user=User(
                    id=UserId(1),
                    username=Username("test"),
                    email=Email("test@test.test"),
                    password=PasswordHash("test"),
                    bio="",
                    image=None,
                ),
                is_followed=True,
            ),
            {
                "profile": {
                    "username": "test",
                    "bio": "",
                    "image": None,
                    "following": True,
                }
            },
        ),
        pytest.param(
            GetProfileResult(
                user=User(
                    id=UserId(1),
                    username=Username("test-2"),
                    email=Email("test-2@test.test"),
                    password=PasswordHash("test-2"),
                    bio="test bio",
                    image=URL("https://test.test/image.jpg"),
                ),
                is_followed=False,
            ),
            {
                "profile": {
                    "username": "test-2",
                    "bio": "test bio",
                    "image": "https://test.test/image.jpg",
                    "following": False,
                }
            },
        ),
    ],
)
async def test_get_profile_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[GetProfileInput, GetProfileResult],
    use_case_result: GetProfileResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.get("/api/v1/profiles/test", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
