__all__ = [
    "ARTICLE_NOT_FOUND_RESPONSE",
    "ArticleModel",
    "ArticleResponseModel",
    "ArticleResponseSchema",
    "ArticleSchema",
    "MultipleArticlesResponseModel",
    "MultipleArticlesResponseSchema",
]

import datetime as dt
import typing as t
from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import web
from marshmallow import Schema, fields

from conduit.api.response import ProfileModel, ProfileSchema
from conduit.core.entities.article import ArticleWithExtra

ARTICLE_NOT_FOUND_RESPONSE: t.Final = web.json_response({"error": "article not found"}, status=HTTPStatus.NOT_FOUND)


@dataclass(frozen=True)
class ArticleModel:
    slug: str
    title: str
    description: str
    body: str
    tag_list: list[str]
    created_at: dt.datetime
    updated_at: dt.datetime
    is_favorite: bool
    favorite_count: int
    author: ProfileModel

    @classmethod
    def new(cls, article: ArticleWithExtra) -> "ArticleModel":
        return ArticleModel(
            slug=article.v.slug,
            title=article.v.title,
            description=article.v.description,
            body=article.v.body,
            tag_list=[str(tag) for tag in article.tags],
            created_at=article.v.created_at.replace(tzinfo=dt.timezone.utc),
            updated_at=(
                article.v.updated_at.replace(tzinfo=dt.timezone.utc)
                if article.v.updated_at is not None
                else article.v.created_at.replace(tzinfo=dt.timezone.utc)
            ),
            is_favorite=article.is_article_favorite,
            favorite_count=article.favorite_of_user_count,
            author=ProfileModel.new(article.author, following=article.is_author_followed),
        )


class ArticleSchema(Schema):
    slug = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String(required=True)
    body = fields.String(required=True)
    tag_list = fields.List(fields.String(), required=True, data_key="tagList")
    created_at = fields.DateTime(required=True, data_key="createdAt")
    updated_at = fields.DateTime(required=True, data_key="updatedAt")
    is_favorite = fields.Boolean(required=True, data_key="favorited")
    favorite_count = fields.Integer(required=True, data_key="favoritesCount")
    author = fields.Nested(ProfileSchema(), required=True)


@dataclass(frozen=True)
class ArticleResponseModel:
    article: ArticleModel

    @classmethod
    def new(cls, article: ArticleWithExtra) -> "ArticleResponseModel":
        return ArticleResponseModel(article=ArticleModel.new(article))

    def response(self, status: HTTPStatus = HTTPStatus.OK) -> web.Response:
        return web.json_response(_ARTICLE_RESPONSE_SCHEMA.dump(self), status=status)


class ArticleResponseSchema(Schema):
    article = fields.Nested(ArticleSchema(), required=True)


@dataclass(frozen=True)
class MultipleArticlesResponseModel:
    articles: list[ArticleModel]
    count: int

    @classmethod
    def new(cls, articles: list[ArticleWithExtra], count: int) -> "MultipleArticlesResponseModel":
        return MultipleArticlesResponseModel(
            articles=[ArticleModel.new(article) for article in articles],
            count=count,
        )

    def response(self) -> web.Response:
        return web.json_response(_MULTIPLE_ARTICLES_RESPONSE_SCHEMA.dump(self))


class MultipleArticlesResponseSchema(Schema):
    articles = fields.List(fields.Nested(ArticleSchema()), required=True)
    count = fields.Integer(required=True, data_key="articlesCount")


_ARTICLE_RESPONSE_SCHEMA = ArticleResponseSchema()
_MULTIPLE_ARTICLES_RESPONSE_SCHEMA = MultipleArticlesResponseSchema()
