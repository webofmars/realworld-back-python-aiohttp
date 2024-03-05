__all__ = [
    "create_article_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, request_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.articles.response import ArticleResponseModel, ArticleResponseSchema
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import Tag
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.create import CreateArticleInput, CreateArticleResult


class CreateArticleSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(max=512))
    description = fields.String(required=True, validate=validate.Length(max=1024))
    body = fields.String(required=True, validate=validate.Length(max=8192))
    tag_list = fields.List(fields.String, validate=validate.Length(max=10), data_key="tagList")

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> CreateArticleInput:
        raw_tags = data.get("tag_list", [])
        return CreateArticleInput(
            token=AuthToken(""),
            user_id=None,
            title=data["title"],
            description=data["description"],
            body=data["body"],
            tags=[Tag(tag) for tag in raw_tags],
        )


class CreateArticleRequestSchema(Schema):
    article = fields.Nested(CreateArticleSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> CreateArticleInput:
        return data["article"]


def create_article_endpoint(use_case: UseCase[CreateArticleInput, CreateArticleResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Create a new article.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @request_schema(CreateArticleRequestSchema, put_into="input")
    @response_schema(ArticleResponseSchema, code=HTTPStatus.CREATED, description="Article successfully created.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, CreateArticleInput)
        input = replace(input, token=request["auth_token"])
        result = await use_case.execute(input)
        response_model = ArticleResponseModel.new(result.article)
        return response_model.response(status=HTTPStatus.CREATED)

    return handler
