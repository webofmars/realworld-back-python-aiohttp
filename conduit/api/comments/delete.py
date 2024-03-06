__all__ = [
    "delete_comment_endpoint",
]

from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, headers_schema, response_schema
from marshmallow import Schema

from conduit.api.auth import RequiredAuthHeaderSchema
from conduit.api.base import Endpoint
from conduit.api.comments.response import COMMENT_NOT_FOUND_RESPONSE
from conduit.api.response import ErrorSchema
from conduit.core.entities.article import ArticleSlug
from conduit.core.entities.comment import CommentId
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.comments.delete import DeleteCommentInput, DeleteCommentResult


class DeleteCommentResponseSchema(Schema):
    pass


def delete_comment_endpoint(use_case: UseCase[DeleteCommentInput, DeleteCommentResult]) -> Endpoint:
    @docs(tags=["comments"], summary="Delete a comment.")
    @headers_schema(RequiredAuthHeaderSchema, put_into="auth_token")
    @response_schema(DeleteCommentResponseSchema, code=HTTPStatus.NO_CONTENT)
    @response_schema(ErrorSchema, code=HTTPStatus.NOT_FOUND, description="Comment not found.")
    @response_schema(ErrorSchema, code=HTTPStatus.FORBIDDEN, description="Permission denied.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="User is not authenticated.")
    async def handler(request: web.Request) -> web.Response:
        auth_token = request["auth_token"]
        article_slug = ArticleSlug(request.match_info["slug"])
        comment_id = CommentId(int(request.match_info["comment_id"]))
        input = DeleteCommentInput(token=auth_token, user_id=None, article_slug=article_slug, comment_id=comment_id)
        result = await use_case.execute(input)
        if result.comment_id is None:
            return COMMENT_NOT_FOUND_RESPONSE
        return web.json_response({}, status=HTTPStatus.NO_CONTENT)

    return handler
