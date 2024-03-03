__all__ = [
    "get_profile_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema
from marshmallow import Schema, fields

from conduit.api.base import Endpoint, ErrorSchema, OptionalAuthHeaderSchema, ProfileSchema, convert_to_profile
from conduit.api.profiles.base import USER_NOT_FOUND_RESPONSE
from conduit.core.entities.user import Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileResult


class GetProfileResponseSchema(Schema):
    profile = fields.Nested(ProfileSchema(), required=True)


def get_profile_endpoint(use_case: UseCase[GetProfileInput, GetProfileResult]) -> Endpoint:
    @docs(tags=["profiles"], summary="Get an user's profile.")
    @headers_schema(OptionalAuthHeaderSchema, put_into="auth_token")
    @response_schema(GetProfileResponseSchema, code=HTTPStatus.OK)
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="User not found.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        username = Username(request.match_info["username"])
        input = GetProfileInput(token=auth_token, user_id=None, username=username)
        result = await use_case.execute(input)
        if result.user is None:
            return USER_NOT_FOUND_RESPONSE
        return web.json_response(convert_to_profile(result.user, result.is_followed), status=HTTPStatus.OK)

    return handler
