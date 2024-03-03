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

from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.profiles.response import ProfileResponseSchema, USER_NOT_FOUND_RESPONSE, ProfileResponseModel
from conduit.api.response import ErrorSchema
from conduit.core.entities.user import Username
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowResult


def unfollow_endpoint(use_case: UseCase[UnfollowInput, UnfollowResult]) -> Endpoint:
    @docs(tags=["profiles"], summary="Unfollow an user.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(ProfileResponseSchema, code=HTTPStatus.OK, description="Successfully unfollowed.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="Invalid credentials.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="User not found.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        username = Username(request.match_info["username"])
        input = UnfollowInput(token=auth_token, user_id=None, username=username)
        result = await use_case.execute(input)
        if result.user is None:
            return USER_NOT_FOUND_RESPONSE
        response_model = ProfileResponseModel.new(result.user, following=False)
        return response_model.response()

    return handler
