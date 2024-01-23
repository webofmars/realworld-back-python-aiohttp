__all__ = [
    "SignUpInput",
    "SignUpResult",
    "SingUpUseCase",
]
from dataclasses import dataclass

from conduit.core.entities.common import Email, RawPassword, Username
from conduit.core.entities.user import (
    AuthToken,
    AuthTokenGenerator,
    CreateUserInput,
    PasswordHasher,
    User,
    UserRepository,
)
from conduit.core.use_cases import UseCase


@dataclass(frozen=True)
class SignUpInput:
    username: Username
    email: Email
    raw_password: RawPassword


@dataclass(frozen=True)
class SignUpResult:
    user: User
    token: AuthToken


class SingUpUseCase(UseCase[SignUpInput, SignUpResult]):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        auth_token_generator: AuthTokenGenerator,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._auth_token_generator = auth_token_generator

    async def execute(self, input: SignUpInput, /) -> SignUpResult:
        """Sign up a new user.

        Raises:
            UsernameAlreadyExistsError: If `input.username` is already taken.
            EmailAlreadyExistsError: If `input.email` is already taken.
        """
        password_hash = await self._password_hasher.hash_password(input.raw_password)
        user = await self._user_repository.create(
            CreateUserInput(
                username=input.username,
                email=input.email,
                password=password_hash,
            )
        )
        auth_token = await self._auth_token_generator.generate_token(user)
        return SignUpResult(user, auth_token)
