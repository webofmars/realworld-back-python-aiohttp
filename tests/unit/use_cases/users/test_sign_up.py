import pytest

from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.user import Email, RawPassword, User, Username
from conduit.core.use_cases.users.sign_up import SignUpInput, SignUpUseCase
from tests.unit.conftest import FakeAuthTokenGenerator, FakePasswordHasher, FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(
    unit_of_work: FakeUnitOfWork,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
) -> SignUpUseCase:
    return SignUpUseCase(unit_of_work, password_hasher, auth_token_generator)


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
    use_case: SignUpUseCase,
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
    existing_user: User,
    input: SignUpInput,
) -> None:
    # Act
    result = await use_case.execute(input)

    # Assert
    assert result.user == existing_user
    assert user_repository.create_input is not None
    assert user_repository.create_input.username == input.username
    assert user_repository.create_input.email == input.email
    assert user_repository.create_input.password == await password_hasher.hash_password(input.raw_password)
    assert await auth_token_generator.get_user_id(result.token) == result.user.id


async def test_sign_up_username_already_exists(
    use_case: SignUpUseCase,
    user_repository: FakeUserRepository,
) -> None:
    # Arrange
    user_repository.create_error = UsernameAlreadyExistsError()

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
    assert user_repository.create_input is not None


async def test_sign_up_email_already_exists(
    use_case: SignUpUseCase,
    user_repository: FakeUserRepository,
) -> None:
    # Arrange
    user_repository.create_error = EmailAlreadyExistsError()

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
    assert user_repository.create_input is not None
