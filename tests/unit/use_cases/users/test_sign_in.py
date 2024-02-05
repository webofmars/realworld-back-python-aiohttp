import pytest

from conduit.core.entities.errors import InvalidCredentialsError
from conduit.core.entities.user import Email, RawPassword, Username
from conduit.core.use_cases.users.sign_in import SignInInput, SignInUseCase
from conduit.core.use_cases.users.sign_up import SignUpInput, SignUpUseCase
from tests.unit.conftest import FakeAuthTokenGenerator, FakePasswordHasher, FakeUserRepository


@pytest.fixture
def use_case(
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
) -> SignInUseCase:
    return SignInUseCase(user_repository, password_hasher, auth_token_generator)


@pytest.fixture
def sign_up_use_case(
    user_repository: FakeUserRepository,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
) -> SignUpUseCase:
    return SignUpUseCase(user_repository, password_hasher, auth_token_generator)


@pytest.mark.parametrize(
    ["existing_users", "input"],
    [
        pytest.param(
            [
                SignUpInput(Username("test-1"), Email("test-1@test.test"), RawPassword("test-password-1")),
            ],
            SignInInput(Email("test-1@test.test"), RawPassword("test-password-1")),
            id="test-1",
        ),
        pytest.param(
            [
                SignUpInput(Username("test-1"), Email("test-1@test.test"), RawPassword("test-password-1")),
                SignUpInput(Username("test-2"), Email("test-2@test.test"), RawPassword("test-password-2")),
                SignUpInput(Username("test-3"), Email("test-3@test.test"), RawPassword("test-password-3")),
            ],
            SignInInput(Email("test-2@test.test"), RawPassword("test-password-2")),
            id="test-2",
        ),
    ],
)
async def test_sign_in_success(
    use_case: SignInUseCase,
    sign_up_use_case: SignUpUseCase,
    auth_token_generator: FakeAuthTokenGenerator,
    existing_users: list[SignUpInput],
    input: SignInInput,
) -> None:
    # Arrange
    for sign_up_input in existing_users:
        await sign_up_use_case.execute(sign_up_input)

    # Act
    result = await use_case.execute(input)

    # Assert
    assert result.user.email == input.email
    assert await auth_token_generator.get_user_id(result.token) == result.user.id


@pytest.mark.parametrize(
    ["existing_users", "input"],
    [
        pytest.param(
            [],
            SignInInput(Email("test-1@test.test"), RawPassword("test-password-1")),
            id="test-1",
        ),
        pytest.param(
            [
                SignUpInput(Username("test-2"), Email("test-2@test.test"), RawPassword("test-password-2")),
            ],
            SignInInput(Email("test-2@test.test"), RawPassword("invalid-password")),
            id="test-2",
        ),
        pytest.param(
            [
                SignUpInput(Username("test-3"), Email("test-3@test.test"), RawPassword("test-password-3")),
            ],
            SignInInput(Email("invalid-email@test.test"), RawPassword("test-password-3")),
            id="test-3",
        ),
        pytest.param(
            [
                SignUpInput(Username("test-4"), Email("test-4@test.test"), RawPassword("test-password-4")),
                SignUpInput(Username("test-5"), Email("test-5@test.test"), RawPassword("test-password-5")),
                SignUpInput(Username("test-6"), Email("test-6@test.test"), RawPassword("test-password-6")),
            ],
            SignInInput(Email("test-4@test.test"), RawPassword("test-password-6")),
            id="test-4",
        ),
    ],
)
async def test_sign_in_invalid_credentials(
    use_case: SignInUseCase,
    sign_up_use_case: SignUpUseCase,
    auth_token_generator: FakeAuthTokenGenerator,
    existing_users: list[SignUpInput],
    input: SignInInput,
) -> None:
    # Arrange
    for sign_up_input in existing_users:
        await sign_up_use_case.execute(sign_up_input)

    # Act
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(input)
