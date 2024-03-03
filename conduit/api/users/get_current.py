__all__ = [
    "get_current_user_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema
from marshmallow import Schema, fields

from conduit.api.base import Endpoint, ErrorSchema, RequiredAuthHeaderSchema, UserSchema
from conduit.api.users.response import convert_to_user_response
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.get_current import GetCurrentUserInput, GetCurrentUserResult


class GetCurrentUserResponseSchema(Schema):
    user = fields.Nested(UserSchema(), required=True)


def get_current_user_endpoint(use_case: UseCase[GetCurrentUserInput, GetCurrentUserResult]) -> Endpoint:
    @docs(tags=["users"], summary="Get the authenticated user.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(GetCurrentUserResponseSchema, code=HTTPStatus.OK)
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        input = GetCurrentUserInput(token=auth_token, user_id=None)
        result = await use_case.execute(input)
        return convert_to_user_response(result.user, result.token)

    return handler
