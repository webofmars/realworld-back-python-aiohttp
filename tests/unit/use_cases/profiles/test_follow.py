import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.profiles.follow import FollowInput, FollowUseCase
from tests.unit.conftest import FakeProfileRepository


@pytest.fixture
def use_case(profile_repository: FakeProfileRepository) -> FollowUseCase:
    return FollowUseCase(profile_repository)


async def test_follow_success(
    use_case: FollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]

    # Act
    result = await use_case.execute(
        FollowInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=existing_user.username,
        )
    )

    # Assert
    assert result.profile is not None
    assert result.profile.username == existing_user.username
    assert result.profile.is_following


async def test_follow_user_not_found(
    use_case: FollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]

    # Act
    input = FollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=Username("not-existing-username"),
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.profile is None


async def test_follow_not_authenticated(
    use_case: FollowUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]

    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(
            FollowInput(
                token=AuthToken("test"),
                user_id=None,
                username=existing_user.username,
            )
        )
