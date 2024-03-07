__all__ = [
    "unfavorite_article_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema

from conduit.api.articles.response import ArticleResponseModel, ArticleResponseSchema, article_not_found
from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.unfavorite import UnfavoriteArticleInput, UnfavoriteArticleResult


def unfavorite_article_endpoint(use_case: UseCase[UnfavoriteArticleInput, UnfavoriteArticleResult]) -> Endpoint:
    @docs(tags=["articles"], summary="Remove an article from the user's favorites.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(ArticleResponseSchema, code=HTTPStatus.OK, description="Successfully removed from the favorites.")
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Article not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        slug = ArticleSlug(request.match_info["slug"])
        input = UnfavoriteArticleInput(token=auth_token, user_id=None, slug=slug)
        result = await use_case.execute(input)
        if result.article is None:
            return article_not_found()
        response_model = ArticleResponseModel.new(result.article)
        return response_model.response()

    return handler
