__all__ = [
    "SignInInput",
    "SignInResult",
    "SignInUseCase",
]
import logging
from dataclasses import dataclass

from conduit.core.entities.common import Email, RawPassword
from conduit.core.entities.errors import InvalidCredentialsError
from conduit.core.entities.user import AuthToken, AuthTokenGenerator, PasswordHasher, User, UserRepository
from conduit.core.use_cases import UseCase

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class SignInInput:
    email: Email
    password: RawPassword


@dataclass(frozen=True)
class SignInResult:
    user: User
    token: AuthToken


class SignInUseCase(UseCase[SignInInput, SignInResult]):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        auth_token_generator: AuthTokenGenerator,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._auth_token_generator = auth_token_generator

    async def execute(self, input: SignInInput, /) -> SignInResult:
        """Sign in with email and password.

        Raises:
            InvalidCredentialsError: If either `input.email` or `input.password` is not valid.
        """
        user = await self._user_repository.get_by_email(input.email)
        if user is None:
            LOG.info("user not found", extra={"email": input.email})
            raise InvalidCredentialsError()
        verification = await self._password_hasher.verify(input.password, user.password)
        if not verification.is_success:
            LOG.info("invalid password", extra={"user_id": user.id})
            raise InvalidCredentialsError()
        auth_token = await self._auth_token_generator.generate_token(user)
        return SignInResult(user, auth_token)
