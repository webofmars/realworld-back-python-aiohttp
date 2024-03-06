__all__ = [
    "favorite_article_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema

from conduit.api.articles.response import ARTICLE_NOT_FOUND_RESPONSE, ArticleResponseModel, ArticleResponseSchema
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.favorite import FavoriteArticleInput, FavoriteArticleResult


def favorite_article_endpoint(use_case: UseCase[FavoriteArticleInput, FavoriteArticleResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Add an article to the user's favorites.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(ArticleResponseSchema, code=HTTPStatus.CREATED, description="Successfully added to the favorites.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Article not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        slug = ArticleSlug(request.match_info["slug"])
        input = FavoriteArticleInput(token=auth_token, user_id=None, slug=slug)
        result = await use_case.execute(input)
        if result.article is None:
            return ARTICLE_NOT_FOUND_RESPONSE
        response_model = ArticleResponseModel.new(result.article)
        return response_model.response()

    return handler
