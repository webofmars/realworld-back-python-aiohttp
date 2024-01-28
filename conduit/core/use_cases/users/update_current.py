__all__ = [
    "UpdateCurrentUserInput",
    "UpdateCurrentUserResult",
    "UpdateCurrentUserUseCase",
]

import logging
from dataclasses import dataclass, replace

from yarl import URL

from conduit.core.entities.common import NotSet
from conduit.core.entities.user import (
    AuthToken,
    Email,
    PasswordHash,
    PasswordHasher,
    RawPassword,
    UpdateUserInput,
    User,
    UserId,
    Username,
    UserRepository,
)
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthenticationInput

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateCurrentUserInput(WithAuthenticationInput):
    username: Username | NotSet = NotSet.NOT_SET
    email: Email | NotSet = NotSet.NOT_SET
    password: RawPassword | NotSet = NotSet.NOT_SET
    bio: str | NotSet = NotSet.NOT_SET
    image: URL | None | NotSet = NotSet.NOT_SET

    def with_user_id(self, id: UserId) -> "UpdateCurrentUserInput":
        return replace(self, user_id=id)

    def convert(self, password: PasswordHash | NotSet) -> UpdateUserInput:
        return UpdateUserInput(
            username=self.username,
            email=self.email,
            password=password,
            bio=self.bio,
            image=self.image,
        )


@dataclass(frozen=True)
class UpdateCurrentUserResult:
    user: User | None
    token: AuthToken


class UpdateCurrentUserUseCase(UseCase[UpdateCurrentUserInput, UpdateCurrentUserResult]):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, input: UpdateCurrentUserInput, /) -> UpdateCurrentUserResult:
        """Update current user.

        Raises:
            UserIsNotAuthenticatedError: If user is not authenticated.
            UserDoesNotExistError: If user does not exist.
            UsernameAlreadyExistsError: If `input.username` is already taken.
            EmailAlreadyExistsError: If `input.email` is already taken.
        """
        user_id = input.ensure_authenticated()
        password_hash: PasswordHash | NotSet = NotSet.NOT_SET
        if input.password is not NotSet.NOT_SET:
            password_hash = await self._password_hasher.hash_password(input.password)
        updated_user = await self._user_repository.update(
            id=user_id,
            input=input.convert(password_hash),
        )
        if updated_user is None:
            LOG.warning("authenticated user not found", extra={"user_id": input.user_id})
        return UpdateCurrentUserResult(updated_user, input.token)
