__all__ = [
    "feed_articles_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, querystring_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.articles.response import MultipleArticlesResponseModel, MultipleArticlesResponseSchema
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.feed import FeedArticlesInput, FeedArticlesResult


class FeedArticlesQueryParamsSchema(Schema):
    limit = fields.Integer(required=False, validate=validate.Range(min=1, max=100))
    offset = fields.Integer(required=False, validate=validate.Range(min=0))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> FeedArticlesInput:
        return FeedArticlesInput(**data, token=AuthToken(""), user_id=None)


def feed_articles_endpoint(use_case: UseCase[FeedArticlesInput, FeedArticlesResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Feed articles.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @querystring_schema(FeedArticlesQueryParamsSchema, put_into="input")
    @response_schema(MultipleArticlesResponseSchema, code=HTTPStatus.OK)
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, FeedArticlesInput)
        input = replace(input, token=request["auth_token"])
        result = await use_case.execute(input)
        response_model = MultipleArticlesResponseModel.new(result.articles, result.count)
        return response_model.response()

    return handler
