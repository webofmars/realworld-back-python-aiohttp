__all__ = [
    "SignUpInput",
    "SingUpUseCase",
]
from dataclasses import dataclass

from conduit.core.entities.common import Email, RawPassword, Username
from conduit.core.use_cases import UseCase


@dataclass(frozen=True)
class SignUpInput:
    username: Username
    email: Email
    raw_password: RawPassword


class SingUpUseCase(UseCase[SignUpInput, None]):
    async def execute(self, input: SignUpInput, /) -> None:
        """Sign up a new user.

        Raises:
            ConnectionError: If no available port is found.
        """
        pass
