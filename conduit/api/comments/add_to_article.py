__all__ = [
    "add_comment_to_article_endpoint",
]

import typing as t
from dataclasses import replace
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, request_schema, response_schema
from marshmallow import Schema, fields, post_load, validate

from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.comments.response import CommentResponseModel, CommentResponseSchema
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.user import AuthToken
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.add_to_article import AddCommentToArticleInput, AddCommentToArticleResult


class AddCommentSchema(Schema):
    body = fields.String(required=True, validate=validate.Length(max=2096))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> AddCommentToArticleInput:
        return AddCommentToArticleInput(
            token=AuthToken(""),
            user_id=None,
            article_slug=ArticleSlug(""),
            body=data["body"],
        )


class AddCommentRequestSchema(Schema):
    comment = fields.Nested(AddCommentSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> AddCommentToArticleInput:
        return data["comment"]


def add_comment_to_article_endpoint(use_case: UseCase[AddCommentToArticleInput, AddCommentToArticleResult]) -> Endpoint:
    @docs(tags=["comments"], summary="Add a new comment to an article.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @request_schema(AddCommentRequestSchema, put_into="input")
    @response_schema(CommentResponseSchema, code=HTTPStatus.CREATED, description="Comment successfully added.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Article not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, AddCommentToArticleInput)
        auth_token = request["auth_token"]
        article_slug = ArticleSlug(request.match_info["slug"])
        input = replace(input, token=auth_token, article_slug=article_slug)
        result = await use_case.execute(input)
        response_model = CommentResponseModel.new(result.comment)
        return response_model.response(status=HTTPStatus.CREATED)

    return handler
