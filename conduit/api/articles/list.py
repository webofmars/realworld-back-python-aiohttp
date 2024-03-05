__all__ = [
    "list_articles_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, querystring_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.articles.response import MultipleArticlesResponseModel, MultipleArticlesResponseSchema
from conduit.api.auth import OptionalAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.core.entities.article import Tag
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.list import ListArticlesInput, ListArticlesResult


class ListArticlesQueryParamsSchema(Schema):
    tag = fields.String(required=False, validate=validate.Length(max=256))
    author = fields.String(required=False, validate=validate.Length(max=128))
    favorite_of = fields.String(required=False, validate=validate.Length(max=128), data_key="favorited")
    limit = fields.Integer(required=False, validate=validate.Range(min=1, max=100))
    offset = fields.Integer(required=False, validate=validate.Range(min=0))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> ListArticlesInput:
        if "tag" in data:
            data["tag"] = Tag(data["tag"])
        return ListArticlesInput(**data, token=None, user_id=None)


def list_articles_endpoint(use_case: UseCase[ListArticlesInput, ListArticlesResult]) -> Endpoint:
    @docs(tags=["articles"], summary="List articles.")
    @headers_schema(OptionalAuthHeaderSchema, put_into="auth_token")
    @querystring_schema(ListArticlesQueryParamsSchema, put_into="input")
    @response_schema(MultipleArticlesResponseSchema, code=HTTPStatus.OK)
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, ListArticlesInput)
        input = replace(input, token=request["auth_token"])
        result = await use_case.execute(input)
        response_model = MultipleArticlesResponseModel.new(result.articles, result.count)
        return response_model.response()

    return handler
