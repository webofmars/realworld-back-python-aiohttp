__all__ = [
    "sign_up_endpoint",
]

import typing as t
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.api.users.response import UserResponseModel, UserResponseSchema
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.sign_up import SignUpInput, SignUpResult


class SignUpUserSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=128))
    email = fields.Email(required=True, validate=validate.Length(max=320))
    password = fields.String(required=True, validate=validate.Length(min=8, max=2048))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> SignUpInput:
        return SignUpInput(
            username=data["username"],
            email=data["email"],
            raw_password=data["password"],
        )


class SignUpRequestSchema(Schema):
    user = fields.Nested(SignUpUserSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> SignUpInput:
        return data["user"]


def sign_up_endpoint(use_case: UseCase[SignUpInput, SignUpResult]) -> Endpoint:
    @docs(tags=["users"], summary="Sign up with email and password.")
    @request_schema(SignUpRequestSchema, put_into="input")
    @response_schema(UserResponseSchema, code=HTTPStatus.CREATED, description="User successfully signed up.")
    @response_schema(ErrorSchema, code=HTTPStatus.BAD_REQUEST, description="Email or username already exists.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, SignUpInput)
        result = await use_case.execute(input)
        response_model = UserResponseModel.new(result.user, result.token)
        return response_model.response(status=HTTPStatus.CREATED)

    return handler
