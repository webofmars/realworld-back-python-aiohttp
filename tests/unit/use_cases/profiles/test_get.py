import pytest

from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileUseCase
from tests.unit.conftest import FakeFollowerRepository, FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> GetProfileUseCase:
    return GetProfileUseCase(unit_of_work)


async def test_get_profile_not_following(
    use_case: GetProfileUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Act
    result = await use_case.execute(
        GetProfileInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=existing_user.username,
        )
    )

    # Assert
    assert result.user is not None
    assert result.user.username == existing_user.username
    assert not result.is_followed


async def test_get_profile_following(
    use_case: GetProfileUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    follower_repository.followers[existing_user.id] = {follower.id}

    # Act
    input = GetProfileInput(
        token=AuthToken("test"),
        user_id=follower.id,
        username=existing_user.username,
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.user is not None
    assert result.user.username == existing_user.username
    assert result.is_followed


async def test_get_profile_not_found(
    use_case: GetProfileUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    user_repository.user = None
    follower_repository.followers[existing_user.id] = {follower.id}

    # Act
    result = await use_case.execute(
        GetProfileInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=Username("not-existing-username"),
        )
    )

    # Assert
    assert result.user is None
    assert user_repository.get_by_username_username == Username("not-existing-username")
