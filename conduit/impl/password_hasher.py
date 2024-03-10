__all__ = [
    "Argon2idPasswordHasher",
]

import asyncio

import argon2
import structlog

from conduit.core.entities.user import PasswordHash, PasswordHasher, RawPassword

LOG = structlog.getLogger(__name__)


class Argon2idPasswordHasher(PasswordHasher):
    """Argon2id password hashing.

    See Also:
        https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
    """

    def __init__(
        self,
        memory_cost: int = 19456,
        time_cost: int = 2,
        parallelism: int = 1,
    ) -> None:
        self._hasher = argon2.PasswordHasher(memory_cost=memory_cost, time_cost=time_cost, parallelism=parallelism)

    async def hash_password(self, password: RawPassword) -> PasswordHash:
        loop = asyncio.get_running_loop()
        hash = await loop.run_in_executor(None, self._hasher.hash, password)
        return PasswordHash(hash)

    async def verify(self, password: RawPassword, hash: PasswordHash) -> bool:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._hasher.verify, hash, password)
        except argon2.exceptions.VerificationError as err:
            LOG.info("invalid password", error=err)
            return False
        return True
