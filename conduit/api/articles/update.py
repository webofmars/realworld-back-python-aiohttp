__all__ = [
    "update_article_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, request_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.articles.response import ARTICLE_NOT_FOUND_RESPONSE, ArticleResponseModel, ArticleResponseSchema
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.common import NotSet
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.update import UpdateArticleInput, UpdateArticleResult


class UpdateArticleSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(max=512))
    description = fields.String(required=False, validate=validate.Length(max=1024))
    body = fields.String(required=False, validate=validate.Length(max=8192))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> UpdateArticleInput:
        return UpdateArticleInput(
            token=AuthToken(""),
            user_id=None,
            slug=ArticleSlug(""),
            title=data.get("title", NotSet.NOT_SET),
            description=data.get("description", NotSet.NOT_SET),
            body=data.get("body", NotSet.NOT_SET),
        )


class UpdateArticleRequestSchema(Schema):
    article = fields.Nested(UpdateArticleSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> UpdateArticleInput:
        return data["article"]


def update_article_endpoint(use_case: UseCase[UpdateArticleInput, UpdateArticleResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Update an article.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @request_schema(UpdateArticleRequestSchema, put_into="input")
    @response_schema(ArticleResponseSchema, code=HTTPStatus.CREATED, description="Article successfully updated.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Article not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.FORBIDDEN, description="Permission denied.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, UpdateArticleInput)
        auth_token = request["auth_token"]
        slug = ArticleSlug(request.match_info["slug"])
        input = replace(input, token=auth_token, slug=slug)
        result = await use_case.execute(input)
        if result.article is None:
            return ARTICLE_NOT_FOUND_RESPONSE
        response_model = ArticleResponseModel.new(result.article)
        return response_model.response()

    return handler
