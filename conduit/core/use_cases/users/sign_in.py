__all__ = [
    "SignInInput",
    "SignInResult",
    "SignInUseCase",
]

from dataclasses import dataclass

import structlog

from conduit.core.entities.errors import InvalidCredentialsError
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import (
    AuthToken,
    AuthTokenGenerator,
    Email,
    PasswordHasher,
    RawPassword,
    User,
)
from conduit.core.use_cases import UseCase

LOG = structlog.get_logger(__name__)


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
        unit_of_work: UnitOfWork,
        password_hasher: PasswordHasher,
        auth_token_generator: AuthTokenGenerator,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._auth_token_generator = auth_token_generator

    async def execute(self, input: SignInInput, /) -> SignInResult:
        """Sign in with email and password.

        Raises:
            InvalidCredentialsError: If either `input.email` or `input.password` is not valid.
        """
        async with self._unit_of_work.begin() as uow:
            user = await uow.users.get_by_email(input.email)
        if user is None:
            LOG.info("user not found", email=input.email)
            raise InvalidCredentialsError()
        is_password_valid = await self._password_hasher.verify(input.password, user.password)
        if not is_password_valid:
            LOG.info("invalid password", user_id=user.id)
            raise InvalidCredentialsError()
        auth_token = await self._auth_token_generator.generate_token(user)
        return SignInResult(user, auth_token)
