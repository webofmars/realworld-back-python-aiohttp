__all__ = [
    "COMMENT_NOT_FOUND_RESPONSE",
    "CommentModel",
    "CommentResponseModel",
    "CommentResponseSchema",
    "CommentSchema",
    "MultipleCommentsResponseModel",
    "MultipleCommentsResponseSchema",
]

import datetime as dt
import typing as t
from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from marshmallow import Schema, fields

from conduit.api.response import ProfileModel, ProfileSchema
from conduit.core.entities.comment import CommentWithExtra

COMMENT_NOT_FOUND_RESPONSE: t.Final = web.json_response({"error": "comment not found"}, status=HTTPStatus.NOT_FOUND)


@dataclass(frozen=True)
class CommentModel:
    id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    body: str
    author: ProfileModel

    @classmethod
    def new(cls, comment: CommentWithExtra) -> "CommentModel":
        return CommentModel(
            id=comment.v.id,
            created_at=comment.v.created_at.replace(tzinfo=dt.timezone.utc),
            updated_at=(
                comment.v.updated_at.replace(tzinfo=dt.timezone.utc)
                if comment.v.updated_at is not None
                else comment.v.created_at.replace(tzinfo=dt.timezone.utc)
            ),
            body=comment.v.body,
            author=ProfileModel.new(comment.author, comment.is_author_followed),
        )


class CommentSchema(Schema):
    id = fields.Integer(required=True)
    created_at = fields.DateTime(required=True, data_key="createdAt")
    updated_at = fields.DateTime(required=True, data_key="updatedAt")
    body = fields.String(required=True)
    author = fields.Nested(ProfileSchema(), required=True)


@dataclass(frozen=True)
class CommentResponseModel:
    comment: CommentModel

    @classmethod
    def new(cls, comment: CommentWithExtra) -> "CommentResponseModel":
        return CommentResponseModel(comment=CommentModel.new(comment))

    def response(self, status: HTTPStatus = HTTPStatus.OK) -> web.Response:
        return web.json_response(_COMMENT_RESPONSE_SCHEMA.dump(self), status=status)


class CommentResponseSchema(Schema):
    comment = fields.Nested(CommentSchema(), required=True)


@dataclass(frozen=True)
class MultipleCommentsResponseModel:
    comments: list[CommentModel]

    @classmethod
    def new(cls, comments: list[CommentWithExtra]) -> "MultipleCommentsResponseModel":
        return MultipleCommentsResponseModel(
            comments=[CommentModel.new(comment) for comment in comments],
        )

    def response(self) -> web.Response:
        return web.json_response(_MULTIPLE_COMMENTS_RESPONSE_SCHEMA.dump(self))


class MultipleCommentsResponseSchema(Schema):
    comments = fields.List(fields.Nested(CommentSchema()), required=True)


_COMMENT_RESPONSE_SCHEMA = CommentResponseSchema()
_MULTIPLE_COMMENTS_RESPONSE_SCHEMA = MultipleCommentsResponseSchema()
