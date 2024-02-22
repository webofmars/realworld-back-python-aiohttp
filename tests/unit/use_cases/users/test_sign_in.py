from dataclasses import replace

import pytest

from conduit.core.entities.errors import InvalidCredentialsError
from conduit.core.entities.user import Email, RawPassword, User
from conduit.core.use_cases.users.sign_in import SignInInput, SignInUseCase
from tests.unit.conftest import FakeAuthTokenGenerator, FakePasswordHasher, FakeUnitOfWork, FakeUserRepository


@pytest.fixture
def use_case(
    unit_of_work: FakeUnitOfWork,
    password_hasher: FakePasswordHasher,
    auth_token_generator: FakeAuthTokenGenerator,
) -> SignInUseCase:
    return SignInUseCase(unit_of_work, password_hasher, auth_token_generator)


@pytest.mark.parametrize(
    "input",
    [
        SignInInput(Email("test-1@test.test"), RawPassword("test-password-1")),
        SignInInput(Email("test-2@test.test"), RawPassword("test-password-2")),
    ],
)
async def test_sign_in_success(
    use_case: SignInUseCase,
    user_repository: FakeUserRepository,
    auth_token_generator: FakeAuthTokenGenerator,
    password_hasher: FakePasswordHasher,
    existing_user: User,
    input: SignInInput,
) -> None:
    # Arrange
    user_repository.user = replace(
        existing_user,
        email=input.email,
        password=await password_hasher.hash_password(input.password),
    )

    # Act
    result = await use_case.execute(input)

    # Assert
    assert result.user.email == input.email
    assert await auth_token_generator.get_user_id(result.token) == result.user.id


@pytest.mark.parametrize(
    "input",
    [
        SignInInput(Email("test-1@test.test"), RawPassword("test-password-1")),
        SignInInput(Email("test-2@test.test"), RawPassword("test-password-2")),
    ],
)
async def test_sign_in_invalid_credentials(
    use_case: SignInUseCase,
    auth_token_generator: FakeAuthTokenGenerator,
    existing_user: User,
    input: SignInInput,
) -> None:
    # Act
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(input)


@pytest.mark.parametrize(
    "input",
    [
        SignInInput(Email("test-1@test.test"), RawPassword("test-password-1")),
        SignInInput(Email("test-2@test.test"), RawPassword("test-password-2")),
    ],
)
async def test_sign_in_user_not_found(
    use_case: SignInUseCase,
    user_repository: FakeUserRepository,
    auth_token_generator: FakeAuthTokenGenerator,
    existing_user: User,
    input: SignInInput,
) -> None:
    # Arrange
    user_repository.user = None

    # Act
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(input)
