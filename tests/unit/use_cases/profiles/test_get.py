import pytest

from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileUseCase
from tests.unit.conftest import FakeProfileRepository


@pytest.fixture
def use_case(profile_repository: FakeProfileRepository) -> GetProfileUseCase:
    return GetProfileUseCase(profile_repository)


@pytest.fixture
def follower() -> User:
    return User(
        id=UserId(123),
        username=Username("follower"),
        email=Email("follower@test.test"),
        password=PasswordHash("test"),
        bio="",
        image=None,
    )


async def test_get_profile_not_following(
    use_case: GetProfileUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]

    # Act
    result = await use_case.execute(
        GetProfileInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=existing_user.username,
        )
    )

    # Assert
    assert result.profile is not None
    assert result.profile.username == existing_user.username
    assert not result.profile.is_following


async def test_get_profile_following(
    use_case: GetProfileUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]
    profile_repository.followers[existing_user.id] = {follower.id}

    # Act
    result = await use_case.execute(
        GetProfileInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=existing_user.username,
        )
    )

    # Assert
    assert result.profile is not None
    assert result.profile.username == existing_user.username
    assert result.profile.is_following


async def test_get_profile_not_found(
    use_case: GetProfileUseCase,
    profile_repository: FakeProfileRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    profile_repository.users = [existing_user]
    profile_repository.followers[existing_user.id] = {follower.id}

    # Act
    result = await use_case.execute(
        GetProfileInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=Username("not-existing-username"),
        )
    )

    # Assert
    assert result.profile is None
