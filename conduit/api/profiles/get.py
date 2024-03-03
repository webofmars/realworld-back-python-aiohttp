__all__ = [
    "get_profile_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema
from marshmallow import Schema, fields

from conduit.api.auth import OptionalAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.profiles.response import ProfileResponseSchema, USER_NOT_FOUND_RESPONSE, ProfileResponseModel
from conduit.api.response import ErrorSchema, ProfileSchema
from conduit.core.entities.user import Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileResult


class GetProfileResponseSchema(Schema):
    profile = fields.Nested(ProfileSchema(), required=True)


def get_profile_endpoint(use_case: UseCase[GetProfileInput, GetProfileResult]) -> Endpoint:
    @docs(tags=["profiles"], summary="Get an user's profile.")
    @headers_schema(OptionalAuthHeaderSchema, put_into="auth_token")
    @response_schema(ProfileResponseSchema, code=HTTPStatus.OK)
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="User not found.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        username = Username(request.match_info["username"])
        input = GetProfileInput(token=auth_token, user_id=None, username=username)
        result = await use_case.execute(input)
        if result.user is None:
            return USER_NOT_FOUND_RESPONSE
        response_model = ProfileResponseModel.new(result.user, result.is_followed)
        return response_model.response()

    return handler
