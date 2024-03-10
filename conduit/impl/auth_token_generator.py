__all__ = [
    "JwtAuthTokenGenerator",
]

import datetime as dt
import typing as t

import jwt
import structlog

from conduit.core.entities.user import AuthToken, AuthTokenGenerator, User, UserId

LOG = structlog.get_logger(__name__)


class JwtAuthTokenGenerator(AuthTokenGenerator):
    ALGORITHM: t.Final = "HS256"

    def __init__(
        self,
        secret_key: str,
        expiration_time: dt.timedelta = dt.timedelta(days=10),
        now: t.Callable[[], dt.datetime] = dt.datetime.utcnow,
    ) -> None:
        self._secret_key = secret_key
        self._expiration_time = expiration_time
        self._now = now

    async def generate_token(self, user: User) -> AuthToken:
        payload = {"user_id": user.id, "exp": self._now() + self._expiration_time}
        token = jwt.encode(payload, self._secret_key, algorithm=self.ALGORITHM)
        return AuthToken(token)

    async def get_user_id(self, token: AuthToken) -> UserId | None:
        try:
            payload = jwt.decode(str(token), self._secret_key, algorithms=[self.ALGORITHM])
        except jwt.InvalidTokenError as err:
            LOG.info("invalid JWT", token=str(token), err=err)
            return None
        user_id = payload["user_id"]
        assert isinstance(user_id, int)
        return UserId(user_id)
