import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowUseCase
from tests.unit.conftest import FakeFollowerRepository, FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(unit_of_work: FakeUnitOfWork) -> UnfollowUseCase:
    return UnfollowUseCase(unit_of_work)


async def test_unfollow_success(
    use_case: UnfollowUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    follower_repository.followers[existing_user.id] = {follower.id}

    # Act
    input = UnfollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=existing_user.username,
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.user is not None
    assert result.user.username == existing_user.username
    assert not await follower_repository.is_followed(existing_user.id, by=follower.id)


async def test_unfollow_user_not_found(
    use_case: UnfollowUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    user_repository.user = None
    follower_repository.followers[existing_user.id] = {follower.id}

    # Act
    input = UnfollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=Username("not-existing-username"),
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.user is None
    assert user_repository.get_by_username_username == Username("not-existing-username")


async def test_unfollow_not_authenticated(
    use_case: UnfollowUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(
            UnfollowInput(
                token=AuthToken("test"),
                user_id=None,
                username=existing_user.username,
            )
        )

    # Assert
    assert user_repository.get_by_username_username is None
