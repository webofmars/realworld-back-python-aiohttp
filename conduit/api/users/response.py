__all__ = [
    "UserResponseModel",
    "UserResponseSchema",
]

from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from marshmallow import Schema, fields

from conduit.core.entities.user import AuthToken, User


@dataclass(frozen=True)
class UserModel:
    token: str
    email: str
    username: str
    bio: str
    image: str | None

    @classmethod
    def new(cls, user: User, token: AuthToken) -> "UserModel":
        return UserModel(
            token=token,
            email=user.email,
            username=user.username,
            bio=user.bio,
            image=str(user.image) if user.image is not None else None,
        )


class UserSchema(Schema):
    token = fields.String(required=True)
    email = fields.Email(required=True)
    username = fields.String(required=True)
    bio = fields.String(required=True)
    image = fields.URL(required=False, allow_none=True)


@dataclass(frozen=True)
class UserResponseModel:
    user: UserModel

    @classmethod
    def new(cls, user: User, token: AuthToken) -> "UserResponseModel":
        return UserResponseModel(user=UserModel.new(user, token))

    def response(self, status: HTTPStatus = HTTPStatus.OK) -> web.Response:
        return web.json_response(data=_SCHEMA.dump(self), status=status)


class UserResponseSchema(Schema):
    user = fields.Nested(UserSchema(), required=True)


_SCHEMA = UserResponseSchema()
