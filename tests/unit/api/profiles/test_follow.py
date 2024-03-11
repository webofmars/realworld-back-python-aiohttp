import pytest
from aiohttp.test_utils import TestClient
from dependency_injector import containers, providers
from yarl import URL

from conduit.container import UseCases
from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.follow import FollowInput, FollowResult
from tests.unit.api.conftest import FakeUseCase

USE_CASE: FakeUseCase[FollowInput, FollowResult] = FakeUseCase()


@containers.override(UseCases)
class FakeUseCasesContainer(containers.DeclarativeContainer):
    follow = providers.Object(USE_CASE)


@pytest.fixture
def use_case_result() -> FollowResult:
    return FollowResult(
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
def use_case(use_case_result: FollowResult) -> UseCase[FollowInput, FollowResult]:
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
            FollowInput(
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
            FollowInput(
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
async def test_follow_endpoint_request(
    client: TestClient,
    use_case: FakeUseCase[FollowInput, FollowResult],
    url_path: str,
    request_headers: dict[str, str],
    expected_input: FollowInput | None,
    expected_status: int,
) -> None:
    # Act
    resp = await client.post(url_path, headers=request_headers)

    # Assert
    assert resp.status == expected_status
    assert use_case.input == expected_input


@pytest.mark.parametrize(
    "use_case_result, expected_response_body",
    [
        pytest.param(
            FollowResult(
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
                    "following": True,
                }
            },
        ),
        pytest.param(
            FollowResult(
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
                    "following": True,
                }
            },
        ),
    ],
)
async def test_follow_endpoint_response(
    client: TestClient,
    use_case: FakeUseCase[FollowInput, FollowResult],
    use_case_result: FollowResult,
    request_headers: dict[str, str],
    expected_response_body: object,
) -> None:
    # Act
    resp = await client.post("/api/v1/profiles/test/follow", headers=request_headers)

    # Assert
    assert await resp.json() == expected_response_body
