__all__ = [
    "get_comments_from_article_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema

from conduit.api.auth import OptionalAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.comments.response import MultipleCommentsResponseModel, MultipleCommentsResponseSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.get_from_article import GetCommentsFromArticleInput, GetCommentsFromArticleResult


def get_comments_from_article_endpoint(
    use_case: UseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult],
) -> Endpoint:
    @docs(tags=["comments"], summary="Get comments from an article.")
    @headers_schema(OptionalAuthHeaderSchema, put_into="auth_token")
    @response_schema(MultipleCommentsResponseSchema, code=HTTPStatus.OK)
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        article_slug = ArticleSlug(request.match_info["slug"])
        input = GetCommentsFromArticleInput(token=auth_token, user_id=None, article_slug=article_slug)
        result = await use_case.execute(input)
        response_model = MultipleCommentsResponseModel.new(result.comments)
        return response_model.response()

    return handler
