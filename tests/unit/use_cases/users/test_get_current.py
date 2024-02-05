import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import User, AuthToken
from conduit.core.use_cases.users.get_current import GetCurrentUserUseCase, GetCurrentUserInput
from tests.unit.conftest import FakeUserRepository


@pytest.fixture
def use_case(user_repository: FakeUserRepository) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(user_repository)


async def test_get_current_user_success(
    use_case: GetCurrentUserUseCase,
    existing_user: User,
    existing_user_auth_token: AuthToken,
) -> None:
    # Act
    result = await use_case.execute(GetCurrentUserInput(token=existing_user_auth_token, user_id=existing_user.id))

    # Assert
    assert result.user == existing_user
    assert result.token == existing_user_auth_token


async def test_get_current_user_not_authenticated(
    use_case: GetCurrentUserUseCase,
    existing_user: User,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(GetCurrentUserInput(token=AuthToken("test"), user_id=None))
