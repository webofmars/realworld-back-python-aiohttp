import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User
from conduit.core.use_cases.users.get_current import GetCurrentUserInput, GetCurrentUserUseCase
from tests.unit.conftest import FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(unit_of_work)


async def test_get_current_user_success(
    use_case: GetCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
    existing_user_auth_token: AuthToken,
) -> None:
    # Act
    result = await use_case.execute(GetCurrentUserInput(token=existing_user_auth_token, user_id=existing_user.id))

    # Assert
    assert user_repository.get_by_id_id == existing_user.id
    assert result.user == existing_user
    assert result.token == existing_user_auth_token


async def test_get_current_user_not_authenticated(
    use_case: GetCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(GetCurrentUserInput(token=AuthToken("test"), user_id=None))

    # Assert
    assert user_repository.get_by_id_id is None
