import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[UnfollowInput, UnfollowResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    unfollow = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> UnfollowResult:
    return UnfollowResult(
        user=User(
            id=UserId(1),
            username=Username("test"),
            email=Email("test@test.test"),
            password=PasswordHash("test"),
            bio="",
            image=None,
        ),
    )


@pytest.fixture
def use_case(use_case_result: UnfollowResult) -> UseCase[UnfollowInput, UnfollowResult]:
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
            "/api/v1/profiles/test/follow",
            {"authorization": "Token test-auth-token"},
            UnfollowInput(
                token=AuthToken("test-auth-token"),
                user_id=None,
                username=Username("test"),
            ),
            200,
            id="1",
        ),
        pytest.param(
            "/api/v1/profiles/test-test-test/follow",
            {"authorization": "Token token"},
            UnfollowInput(
                token=AuthToken("token"),
                user_id=None,
                username=Username("test-test-test"),
            ),
            200,
            id="2",
        ),
        pytest.param(
            "/api/v1/profiles/test-test-test/follow",
            {},
            None,
            422,
            id="3",
        ),
    ],
)
async def test_unfollow_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[UnfollowInput, UnfollowResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: UnfollowInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.delete(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            UnfollowResult(
                user=User(
                    id=UserId(1),
                    username=Username("test"),
                    email=Email("test@test.test"),
                    password=PasswordHash("test"),
                    bio="",
                    image=None,
                ),
            ),
            {
                "profile": {
                    "username": "test",
                    "bio": "",
                    "image": None,
                    "following": False,
                }
            },
        ),
        pytest.param(
            UnfollowResult(
                user=User(
                    id=UserId(1),
                    username=Username("test-2"),
                    email=Email("test-2@test.test"),
                    password=PasswordHash("test-2"),
                    bio="test bio",
                    image=URL("https://test.test/image.jpg"),
                ),
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
async def test_unfollow_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[UnfollowInput, UnfollowResult],
    use_case_result: UnfollowResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.delete("/api/v1/profiles/test/follow", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
