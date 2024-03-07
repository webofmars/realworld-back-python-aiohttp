__all__ = [
    "list_tags_endpoint",
]

from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import docs, response_schema
from marshmallow import Schema, fields

from conduit.api.base import Endpoint
from conduit.core.entities.article import Tag
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.tags.list import ListTagsInput, ListTagsResult


@dataclass(frozen=True)
class TagsResponseModel:
    tags: list[str]

    @classmethod
    def new(cls, tags: list[Tag]) -> "TagsResponseModel":
        return TagsResponseModel([str(tag) for tag in tags])

    def response(self) -> web.Response:
        return web.json_response(TagsResponseSchema().dump(self))


class TagsResponseSchema(Schema):
    tags = fields.List(fields.String, required=True)


def list_tags_endpoint(use_case: UseCase[ListTagsInput, ListTagsResult]) -> Endpoint:
    @docs(tags=["tags"], summary="List all tags.")
    @response_schema(TagsResponseSchema, code=HTTPStatus.OK)
    async def handler(_: web.Request) -> web.Response:
        input = ListTagsInput()
        result = await use_case.execute(input)
        response_model = TagsResponseModel.new(result.tags)
        return response_model.response()

    return handler
