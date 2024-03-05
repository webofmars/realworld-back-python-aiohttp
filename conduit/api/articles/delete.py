__all__ = [
    "delete_article_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema
from marshmallow import Schema

from conduit.api.articles.response import ARTICLE_NOT_FOUND_RESPONSE
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.delete import DeleteArticleInput, DeleteArticleResult


class DeleteArticleResponseSchema(Schema):
    pass


def delete_article_endpoint(use_case: UseCase[DeleteArticleInput, DeleteArticleResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Delete an article.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(DeleteArticleResponseSchema, code=HTTPStatus.NO_CONTENT)
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Article not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.FORBIDDEN, description="Permission denied.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        slug = ArticleSlug(request.match_info["slug"])
        input = DeleteArticleInput(token=auth_token, user_id=None, slug=slug)
        result = await use_case.execute(input)
        if result.id is None:
            return ARTICLE_NOT_FOUND_RESPONSE
        return web.json_response({}, status=HTTPStatus.NO_CONTENT)

    return handler
