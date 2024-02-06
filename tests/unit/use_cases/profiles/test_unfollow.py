import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowUseCase
from tests.unit.conftest import FakeProfileRepository


@pytest.fixture
def use_case(profile_repository: FakeProfileRepository) -> UnfollowUseCase:
    return UnfollowUseCase(profile_repository)


async def test_unfollow_success(
    use_case: UnfollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]
    profile_repository.followers[existing_user.id] = {follower.id}

    # Act
    input = UnfollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=existing_user.username,
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.profile is not None
    assert result.profile.username == existing_user.username
    assert not result.profile.is_following


async def test_unfollow_user_not_found(
    use_case: UnfollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]
    profile_repository.followers[existing_user.id] = {follower.id}

    # Act
    input = UnfollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=Username("not-existing-username"),
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.profile is None


async def test_follow_not_authenticated(
    use_case: UnfollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]

    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(
            UnfollowInput(
                token=AuthToken("test"),
                user_id=None,
                username=existing_user.username,
            )
        )
