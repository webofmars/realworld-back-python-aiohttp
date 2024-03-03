__all__ = [
    "unfollow_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import (
    docs,
    headers_schema,
    response_schema,
)
from marshmallow import Schema, fields

from conduit.api.base import Endpoint, ErrorSchema, ProfileSchema, RequiredAuthHeaderSchema, convert_to_profile
from conduit.api.profiles.base import USER_NOT_FOUND_RESPONSE
from conduit.core.entities.user import Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowResult


class UnfollowResponseSchema(Schema):
    profile = fields.Nested(ProfileSchema(), required=True)


def unfollow_endpoint(use_case: UseCase[UnfollowInput, UnfollowResult]) -> Endpoint:
    @docs(tags=["profiles"], summary="Unfollow an user.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(UnfollowResponseSchema, code=HTTPStatus.OK, description="Successfully unfollowed.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="Invalid credentials.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="User not found.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        username = Username(request.match_info["username"])
        input = UnfollowInput(token=auth_token, user_id=None, username=username)
        result = await use_case.execute(input)
        if result.user is None:
            return USER_NOT_FOUND_RESPONSE
        return web.json_response(convert_to_profile(result.user, following=False))

    return handler
