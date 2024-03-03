__all__ = [
    "Endpoint",
    "ErrorSchema",
    "OptionalAuthHeaderSchema",
    "RequiredAuthHeaderSchema",
    "UserSchema",
]

import typing as t

from aiohttp import web
from marshmallow import Schema, ValidationError, fields, post_load, validate, validates

from conduit.core.entities.user import AuthToken

AUTH_HEADER_PREFIX: t.Final = "Token "


Endpoint = t.Callable[[web.Request], t.Awaitable[web.Response]]


class RequiredAuthHeaderSchema(Schema):
    authorization = fields.String(required=True, validate=validate.Length(max=1024))

    @validates("authorization")
    def validate_auth_token(self, value: str) -> None:
        if not value.startswith(AUTH_HEADER_PREFIX):
            raise ValidationError("invalid authorization header")

    @post_load
    def to_auth_token(self, data: dict[str, t.Any], **_: t.Any) -> AuthToken:
        _, _, token = data["authorization"].partition(" ")
        return AuthToken(token)


class OptionalAuthHeaderSchema(Schema):
    authorization = fields.String(required=False, load_default=None, validate=validate.Length(max=1024))

    @validates("authorization")
    def validate_auth_token(self, value: t.Optional[str]) -> None:
        if value is None:
            return None
        if not value.startswith(AUTH_HEADER_PREFIX):
            raise ValidationError("invalid authorization header")

    @post_load
    def to_auth_token(self, data: dict[str, t.Any], **_: t.Any) -> AuthToken | None:
        raw_token = data.get("authorization")
        if raw_token is None:
            return None
        _, _, token = raw_token.partition(" ")
        return AuthToken(token)


class ErrorSchema(Schema):
    error = fields.String(required=True)


class UserSchema(Schema):
    email = fields.Email(required=True)
    token = fields.String(required=True)
    username = fields.String(required=True)
    bio = fields.String(required=True)
    image = fields.URL(required=False, allow_none=True)
