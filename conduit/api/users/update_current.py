__all__ = [
    "update_current_user_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, json_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.api.users.response import UserResponseModel, UserResponseSchema
from conduit.core.entities.common import NotSet
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.update_current import UpdateCurrentUserInput, UpdateCurrentUserResult


class UpdateCurrentUserSchema(Schema):
    username = fields.String(required=False, validate=validate.Length(min=3, max=128))
    email = fields.Email(required=False, validate=validate.Length(max=320))
    password = fields.String(required=False, validate=validate.Length(min=8, max=2048))
    bio = fields.String(required=False, validate=validate.Length(max=4096))
    image = fields.URL(required=False, allow_none=True, validate=validate.Length(max=1024))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> UpdateCurrentUserInput:
        return UpdateCurrentUserInput(
            token=AuthToken(""),
            user_id=None,
            username=data.get("username", NotSet.NOT_SET),
            email=data.get("email", NotSet.NOT_SET),
            password=data.get("password", NotSet.NOT_SET),
            bio=data.get("bio", NotSet.NOT_SET),
            image=data.get("image", NotSet.NOT_SET),
        )


class UpdateCurrentUserRequestSchema(Schema):
    user = fields.Nested(UpdateCurrentUserSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> UpdateCurrentUserInput:
        return data["user"]


def update_current_user_endpoint(use_case: UseCase[UpdateCurrentUserInput, UpdateCurrentUserResult]) -> Endpoint:
    @docs(tags=["users"], summary="Update the authenticated user.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @json_schema(UpdateCurrentUserRequestSchema, put_into="input")
    @response_schema(UserResponseSchema, code=HTTPStatus.OK)
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    @response_schema(ErrorSchema, code=HTTPStatus.BAD_REQUEST, description="Email or username already exists.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, UpdateCurrentUserInput)
        input = replace(input, token=request["auth_token"])
        result = await use_case.execute(input)
        response_model = UserResponseModel.new(result.user, result.token)
        return response_model.response()

    return handler
