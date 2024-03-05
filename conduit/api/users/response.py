__all__ = [
    "UserResponseModel",
    "UserResponseSchema",
]

from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from marshmallow import Schema, fields

from conduit.api.response import UserModel, UserSchema
from conduit.core.entities.user import AuthToken, User


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
