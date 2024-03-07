__all__ = [
    "ProfileResponseModel",
    "ProfileResponseSchema",
    "user_not_found",
]

from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from marshmallow import Schema, fields

from conduit.api.response import ProfileModel, ProfileSchema
from conduit.core.entities.user import User


def user_not_found() -> web.Response:
    return web.json_response({"error": "user not found"}, status=HTTPStatus.NOT_FOUND)


@dataclass(frozen=True)
class ProfileResponseModel:
    profile: ProfileModel

    @classmethod
    def new(cls, user: User, following: bool) -> "ProfileResponseModel":
        return ProfileResponseModel(profile=ProfileModel.new(user, following))

    def response(self) -> web.Response:
        return web.json_response(_SCHEMA.dump(self))


class ProfileResponseSchema(Schema):
    profile = fields.Nested(ProfileSchema(), required=True)


_SCHEMA = ProfileResponseSchema()
