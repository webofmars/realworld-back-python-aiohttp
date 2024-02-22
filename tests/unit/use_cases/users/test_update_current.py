import pytest
from yarl import URL

from conduit.core.entities.errors import (
    EmailAlreadyExistsError,
    UserIsNotAuthenticatedError,
    UsernameAlreadyExistsError,
)
from conduit.core.entities.user import AuthToken, Email, RawPassword, User, Username
from conduit.core.use_cases.users.update_current import UpdateCurrentUserInput, UpdateCurrentUserUseCase
from tests.unit.conftest import FakePasswordHasher, FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(
    unit_of_work: FakeUnitOfWork,
    password_hasher: FakePasswordHasher,
) -> UpdateCurrentUserUseCase:
    return UpdateCurrentUserUseCase(unit_of_work, password_hasher)


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
    user_repository: FakeUserRepository,
    existing_user: User,
    input: UpdateCurrentUserInput,
    expected_attrs: list[tuple[str, object]],
) -> None:
    # Act
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.user == existing_user
    assert user_repository.update_id == existing_user.id
    for attr_name, attr_value in expected_attrs:
        assert user_repository.update_input is not None
        assert getattr(user_repository.update_input, attr_name) == attr_value, attr_name


async def test_update_current_user_update_password(
    use_case: UpdateCurrentUserUseCase,
    password_hasher: FakePasswordHasher,
    user_repository: FakeUserRepository,
    existing_user: User,
    existing_user_auth_token: AuthToken,
) -> None:
    # Act
    input = UpdateCurrentUserInput(
        token=existing_user_auth_token,
        user_id=None,
        password=RawPassword("new-password"),
    )
    result = await use_case.execute(input.with_user_id(existing_user.id))

    # Assert
    assert result.user == existing_user
    assert user_repository.update_id == existing_user.id
    assert user_repository.update_input is not None
    assert user_repository.update_input.password == await password_hasher.hash_password(RawPassword("new-password"))


async def test_update_current_user_not_authenticated(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Act
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=None,
        bio="new bio",
    )
    with pytest.raises(UserIsNotAuthenticatedError):
        await use_case.execute(input)

    # Assert
    assert user_repository.update_id is None


async def test_update_current_user_username_already_exists(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Arrange
    user_repository.update_error = UsernameAlreadyExistsError()

    # Act
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=existing_user.id,
        username=existing_user.username,
    )
    with pytest.raises(UsernameAlreadyExistsError):
        await use_case.execute(input)

    # Assert
    assert user_repository.update_id == existing_user.id


async def test_update_current_user_email_already_exists(
    use_case: UpdateCurrentUserUseCase,
    user_repository: FakeUserRepository,
    existing_user: User,
) -> None:
    # Arrange
    user_repository.update_error = EmailAlreadyExistsError()

    # Act
    input = UpdateCurrentUserInput(
        token=AuthToken("test"),
        user_id=existing_user.id,
        email=existing_user.email,
    )
    with pytest.raises(EmailAlreadyExistsError):
        await use_case.execute(input)

    # Assert
    assert user_repository.update_id == existing_user.id
