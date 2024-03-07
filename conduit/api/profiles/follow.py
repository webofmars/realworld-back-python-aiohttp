__all__ = [
    "follow_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import (
    docs,
    headers_schema,
    response_schema,
)

from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.profiles.response import ProfileResponseModel, ProfileResponseSchema, user_not_found
from conduit.api.response import ErrorSchema
from conduit.core.entities.user import Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.follow import FollowInput, FollowResult


def follow_endpoint(use_case: UseCase[FollowInput, FollowResult]) -> Endpoint:
    @docs(tags=["profiles"], summary="Follow an user.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(ProfileResponseSchema, code=HTTPStatus.OK, description="Successfully followed.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="Invalid credentials.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="User not found.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        username = Username(request.match_info["username"])
        input = FollowInput(token=auth_token, user_id=None, username=username)
        result = await use_case.execute(input)
        if result.user is None:
            return user_not_found()
        response_model = ProfileResponseModel.new(result.user, following=True)
        return response_model.response()

    return handler
