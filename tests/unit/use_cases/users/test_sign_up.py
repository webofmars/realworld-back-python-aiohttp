import pytest

from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.user import CreateUserInput, Email, PasswordHash, RawPassword, Username
from conduit.core.use_cases.users.sign_up import SignUpInput, SingUpUseCase
from tests.unit.conftest import FakeAuthTokenGenerator, FakePasswordHasher, FakeUserRepository


@pytest.fixture
def use_case(
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
) -> SingUpUseCase:
    return SingUpUseCase(user_repository, password_hasher, auth_token_generator)


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(
            SignUpInput(
                username=Username("test-1"),
                email=Email("test-1@test.test"),
                raw_password=RawPassword("test-1-password"),
            ),
            id="test-1",
        ),
        pytest.param(
            SignUpInput(
                username=Username("test-2"),
                email=Email("test-2@test.test"),
                raw_password=RawPassword("test-2-password"),
            ),
            id="test-2",
        ),
    ],
)
async def test_sign_up_success(
    use_case: SingUpUseCase,
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
    input: SignUpInput,
) -> None:
    # Act
    result = await use_case.execute(input)

    # Assert
    assert result.user.username == input.username
    assert result.user.email == input.email
    assert result.user.bio == ""
    assert result.user.image is None
    assert await password_hasher.verify(input.raw_password, result.user.password)
    assert await user_repository.get_by_id(result.user.id) == result.user
    assert await auth_token_generator.get_user_id(result.token) == result.user.id


async def test_sign_up_username_already_exists(
    use_case: SingUpUseCase,
    user_repository: FakeUserRepository,
) -> None:
    # Arrange
    await user_repository.create(
        CreateUserInput(
            username=Username("test"), email=Email("test@test.test"), password=PasswordHash("test-password-hash")
        )
    )

    # Act
    with pytest.raises(UsernameAlreadyExistsError):
        await use_case.execute(
            SignUpInput(
                username=Username("test"),
                email=Email("another-test-email@test.test"),
                raw_password=RawPassword("test-password"),
            )
        )

    # Assert
    assert await user_repository.get_by_email(Email("another-test-email@test.test")) is None


async def test_sign_up_email_already_exists(
    use_case: SingUpUseCase,
    user_repository: FakeUserRepository,
) -> None:
    # Arrange
    await user_repository.create(
        CreateUserInput(
            username=Username("test-1"), email=Email("test@test.test"), password=PasswordHash("test-password-hash")
        )
    )

    # Act
    with pytest.raises(EmailAlreadyExistsError):
        await use_case.execute(
            SignUpInput(
                username=Username("test-2"),
                email=Email("test@test.test"),
                raw_password=RawPassword("test-password"),
            )
        )

    # Assert
    user = await user_repository.get_by_email(Email("test@test.test"))
    assert user is not None
    assert user.username == Username("test-1")
