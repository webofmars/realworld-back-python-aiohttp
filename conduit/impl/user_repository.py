__all__ = [
    "PostgresqlUserRepository",
]

import datetime as dt
import re
import typing as t

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine
from yarl import URL

from conduit.core.entities.common import NotSet
from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.user import (
    CreateUserInput,
    Email,
    PasswordHash,
    UpdateUserInput,
    User,
    UserId,
    Username,
    UserRepository,
)
from conduit.db import tables


class PostgresqlUserRepository(UserRepository):
    USERNAME_UNIQUE_VIOLATION_RE: t.Final = re.compile(r"Key \(username\)=\(.+\) already exists\.$")
    EMAIL_UNIQUE_VIOLATION_RE: t.Final = re.compile(r"Key \(email\)=\(.+\) already exists\.$")

    def __init__(
        self,
        engine: AsyncEngine,
        now: t.Callable[[], dt.datetime] = dt.datetime.utcnow,
    ) -> None:
        self._engine = engine
        self._now = now

    async def create(self, input: CreateUserInput) -> User:
        stmt = (
            sa.insert(tables.USER)
            .values(
                username=input.username,
                email=input.email,
                password_hash=input.password,
                bio="",
                created_at=self._now(),
            )
            .returning(tables.USER)
        )
        async with self._engine.begin() as connection:
            try:
                result = await connection.execute(stmt)
            except IntegrityError as e:
                self._handle_integrity_error(e)
            row = result.one()
            return self._decode_user(row)

    async def get_by_email(self, email: Email) -> User | None:
        stmt = sa.select(tables.USER).where(tables.USER.c.email == email)
        async with self._engine.connect() as connection:
            result = await connection.execute(stmt)
            row = result.one_or_none()
            if row is None:
                return None
            return self._decode_user(row)

    async def get_by_id(self, id: UserId) -> User | None:
        stmt = sa.select(tables.USER).where(tables.USER.c.id == id)
        async with self._engine.connect() as connection:
            result = await connection.execute(stmt)
            row = result.one_or_none()
            if row is None:
                return None
            return self._decode_user(row)

    async def update(self, id: UserId, input: UpdateUserInput) -> User | None:
        stmt = (
            sa.update(tables.USER).where(tables.USER.c.id == id).values(updated_at=self._now()).returning(tables.USER)
        )
        if input.username is not NotSet.NOT_SET:
            stmt = stmt.values(username=input.username)
        if input.email is not NotSet.NOT_SET:
            stmt = stmt.values(email=input.email)
        if input.password is not NotSet.NOT_SET:
            stmt = stmt.values(password_hash=input.password)
        if input.bio is not NotSet.NOT_SET:
            stmt = stmt.values(bio=input.bio)
        if input.image is not NotSet.NOT_SET:
            stmt = stmt.values(image_url=str(input.image) if input.image is not None else None)
        async with self._engine.begin() as connection:
            try:
                result = await connection.execute(stmt)
            except IntegrityError as e:
                self._handle_integrity_error(e)
            row = result.one_or_none()
            if row is None:
                return None
            return self._decode_user(row)

    def _decode_user(self, db_row: t.Any) -> User:
        return User(
            id=UserId(db_row.id),
            username=Username(db_row.username),
            email=Email(db_row.email),
            password=PasswordHash(db_row.password_hash),
            bio=db_row.bio,
            image=URL(db_row.image_url) if db_row.image_url is not None else None,
        )

    def _handle_integrity_error(self, error: IntegrityError) -> t.NoReturn:
        if error.orig is not None:
            if self.USERNAME_UNIQUE_VIOLATION_RE.search(error.orig.args[0]):
                raise UsernameAlreadyExistsError() from error
            if self.EMAIL_UNIQUE_VIOLATION_RE.search(error.orig.args[0]):
                raise EmailAlreadyExistsError() from error
        raise
