__all__ = [
    "UpdateCurrentUserInput",
    "UpdateCurrentUserResult",
    "UpdateCurrentUserUseCase",
]
import logging
from dataclasses import dataclass, replace

from yarl import URL

from conduit.core.entities.common import Email, NotSet, PasswordHash, RawPassword, Username
from conduit.core.entities.errors import UserDoesNotExistError, UserIsNotAuthenticatedError
from conduit.core.entities.user import AuthToken, PasswordHasher, UpdateUserInput, User, UserId, UserRepository
from conduit.core.use_cases import UseCase

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateCurrentUserInput:
    token: AuthToken
    user_id: UserId | None
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
    user: User
    token: AuthToken


class UpdateCurrentUserUseCase(UseCase[UpdateCurrentUserInput, UpdateCurrentUserResult]):
    """Update current user.

    Raises:
        UserIsNotAuthenticatedError: If user is not authenticated.
        UserDoesNotExistError: If user does not exist.
        UsernameAlreadyExistsError: If `input.username` is already taken.
        EmailAlreadyExistsError: If `input.email` is already taken.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, input: UpdateCurrentUserInput, /) -> UpdateCurrentUserResult:
        if input.user_id is None:
            LOG.info("user is not authenticated")
            raise UserIsNotAuthenticatedError()
        password_hash: PasswordHash | NotSet = NotSet.NOT_SET
        if input.password is not NotSet.NOT_SET:
            password_hash = await self._password_hasher.hash_password(input.password)
        updated_user = await self._user_repository.update(
            id=input.user_id,
            input=input.convert(password_hash),
        )
        if updated_user is None:
            LOG.warning("authenticated user not found", extra={"user_id": input.user_id})
            raise UserDoesNotExistError()
        return UpdateCurrentUserResult(updated_user, input.token)
