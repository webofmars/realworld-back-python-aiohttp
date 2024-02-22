import pytest

from conduit.core.entities.errors import UserIsNotAuthenticatedError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import AuthToken, User, Username
from conduit.core.use_cases.profiles.follow import FollowInput, FollowUseCase
from tests.unit.conftest import FakeFollowerRepository, FakeUserRepository


@pytest.fixture
def use_case(unit_of_work: UnitOfWork) -> FollowUseCase:
    return FollowUseCase(unit_of_work)


async def test_follow_success(
    use_case: FollowUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Act
    result = await use_case.execute(
        FollowInput(
            token=AuthToken("test"),
            user_id=follower.id,
            username=existing_user.username,
        )
    )

    # Assert
    assert result.user is not None
    assert result.user.username == existing_user.username
    assert user_repository.get_by_username_username == existing_user.username
    assert await follower_repository.is_followed(existing_user.id, by=follower.id)


async def test_follow_user_not_found(
    use_case: FollowUseCase,
    user_repository: FakeUserRepository,
    follower_repository: FakeFollowerRepository,
    existing_user: User,
    follower: User,
) -> None:
    # Arrange
    user_repository.user = None

    # Act
    input = FollowInput(
        token=AuthToken("test"),
        user_id=None,
        username=Username("not-existing-username"),
    )
    result = await use_case.execute(input.with_user_id(follower.id))

    # Assert
    assert result.user is None
    assert user_repository.get_by_username_username == Username("not-existing-username")
    assert not await follower_repository.is_followed(existing_user.id, by=follower.id)


async def test_follow_not_authenticated(
    use_case: FollowUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(
            FollowInput(
                token=AuthToken("test"),
                user_id=None,
                username=existing_user.username,
            )
        )

    # Assert
    assert user_repository.get_by_username_username is None
