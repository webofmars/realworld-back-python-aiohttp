import pytest
from yarl import URL

from conduit.core.entities.errors import (
    EmailAlreadyExistsError,
    UserIsNotAuthenticatedError,
    UsernameAlreadyExistsError,
)
from conduit.core.entities.user import AuthToken, Email, RawPassword, User, Username
from conduit.core.use_cases.users.update_current import UpdateCurrentUserInput, UpdateCurrentUserUseCase
from tests.unit.conftest import FakePasswordHasher, FakeUserRepository


@pytest.fixture
def use_case(
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
) -> UpdateCurrentUserUseCase:
    return UpdateCurrentUserUseCase(user_repository, password_hasher)


@pytest.mark.parametrize(
    "input, expected_attrs",
    [
        pytest.param(
            UpdateCurrentUserInput(
                token=AuthToken("test"),
                user_id=None,
                username=Username("new-username"),
            ),
            [
                ("username", Username("new-username")),
            ],
            id="test-1",
        ),
        pytest.param(
            UpdateCurrentUserInput(
                token=AuthToken("test"),
                user_id=None,
                email=Email("new-email@test.test"),
            ),
            [
                ("email", Email("new-email@test.test")),
            ],
            id="test-2",
        ),
        pytest.param(
            UpdateCurrentUserInput(
                token=AuthToken("test"),
                user_id=None,
                bio="new bio",
                image=URL("https://example.org/test-image.jpg"),
            ),
            [
                ("bio", "new bio"),
                ("image", URL("https://example.org/test-image.jpg")),
            ],
            id="test-3",
        ),
        pytest.param(
            UpdateCurrentUserInput(
                token=AuthToken("test"),
                user_id=None,
                username=Username("new-username"),
                email=Email("new-email@test.test"),
                bio="new bio",
                image=URL("https://example.org/test-image.jpg"),
            ),
            [
                ("username", Username("new-username")),
                ("email", Email("new-email@test.test")),
                ("bio", "new bio"),
                ("image", URL("https://example.org/test-image.jpg")),
            ],
            id="test-4",
        ),
    ],
)
async def test_update_current_user_success(
    use_case: UpdateCurrentUserUseCase,
    existing_user: User,
    input: UpdateCurrentUserInput,
    expected_attrs: list[tuple[str, object]],
) -> None:
    # Arrange
    input = input.with_user_id(existing_user.id)

    # Act
    result = await use_case.execute(input)

    # Assert
    for attr_name, attr_value in expected_attrs:
        assert getattr(result.user, attr_name) != getattr(existing_user, attr_name), attr_name
        assert getattr(result.user, attr_name) == attr_value, attr_name


async def test_update_current_user_update_password(
    use_case: UpdateCurrentUserUseCase,
    password_hasher: FakePasswordHasher,
    existing_user: User,
    existing_user_auth_token: AuthToken,
) -> None:
    # Arrange
    input = UpdateCurrentUserInput(
        token=existing_user_auth_token,
        user_id=existing_user.id,
        password=RawPassword("new-password"),
    )

    # Act
    result = await use_case.execute(input)

    # Assert
    assert result.user is not None
    assert result.user.password != existing_user.password
    assert result.user.password == await password_hasher.hash_password(RawPassword("new-password"))


async def test_update_current_user_not_authenticated(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Arrange
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=None,
        bio="new bio",
    )

    # Act
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(input)

    # Assert
    assert await user_repository.get_by_id(existing_user.id) == existing_user


async def test_update_current_user_username_already_exists(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Arrange
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=existing_user.id,
        username=existing_user.username,
    )

    # Act
    with pytest.raises(UsernameAlreadyExistsError):
        await use_case.execute(input)

    # Assert
    assert await user_repository.get_by_id(existing_user.id) == existing_user


async def test_update_current_user_email_already_exists(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Arrange
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=existing_user.id,
        email=existing_user.email,
    )

    # Act
    with pytest.raises(EmailAlreadyExistsError):
        await use_case.execute(input)

    # Assert
    assert await user_repository.get_by_id(existing_user.id) == existing_user
