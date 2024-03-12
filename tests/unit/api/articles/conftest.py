__all__ = [
    "ARTICLE_1",
    "ARTICLE_2",
    "EXPECTED_SERIALIZED_ARTICLE_1",
    "EXPECTED_SERIALIZED_ARTICLE_2",
]

import datetime as dt

from yarl import URL

from conduit.core.entities.article import Article, ArticleId, ArticleSlug, ArticleWithExtra, Tag
from conduit.core.entities.user import Email, PasswordHash, User, UserId, Username

ARTICLE_1 = ArticleWithExtra(
    v=Article(
        id=ArticleId(123),
        author_id=UserId(101),
        slug=ArticleSlug("test-article-slug"),
        title="test-article-title",
        description="test-article-description",
        body="test-article-body",
        created_at=dt.datetime(2020, 1, 2, 3, 4, 5, 123456),
        updated_at=None,
    ),
    author=User(
        id=UserId(101),
        username=Username("test"),
        email=Email("test@test.test"),
        password=PasswordHash("test"),
        bio="",
        image=None,
    ),
    tags=[Tag("test-tag-1"), Tag("test-tag-2")],
    is_author_followed=False,
    is_article_favorite=False,
    favorite_of_user_count=0,
)
ARTICLE_2 = ArticleWithExtra(
    v=Article(
        id=ArticleId(345),
        author_id=UserId(202),
        slug=ArticleSlug("test-article-slug-2"),
        title="test-article-title-2",
        description="test-article-description-2",
        body="test-article-body-2",
        created_at=dt.datetime(2020, 1, 2, 3, 4, 5, 123456),
        updated_at=dt.datetime(2020, 2, 3, 4, 5, 6, 123456),
    ),
    author=User(
        id=UserId(202),
        username=Username("test-2"),
        email=Email("test@test.test"),
        password=PasswordHash("test"),
        bio="test bio",
        image=URL("https://test.test/image.jpg"),
    ),
    tags=[],
    is_author_followed=True,
    is_article_favorite=True,
    favorite_of_user_count=123,
)

EXPECTED_SERIALIZED_ARTICLE_1 = {
    "slug": "test-article-slug",
    "title": "test-article-title",
    "description": "test-article-description",
    "body": "test-article-body",
    "tagList": ["test-tag-1", "test-tag-2"],
    "createdAt": "2020-01-02T03:04:05.123456+00:00",
    "updatedAt": "2020-01-02T03:04:05.123456+00:00",
    "favorited": False,
    "favoritesCount": 0,
    "author": {
        "username": "test",
        "bio": "",
        "image": None,
        "following": False,
    },
}
EXPECTED_SERIALIZED_ARTICLE_2 = {
    "slug": "test-article-slug-2",
    "title": "test-article-title-2",
    "description": "test-article-description-2",
    "body": "test-article-body-2",
    "tagList": [],
    "createdAt": "2020-01-02T03:04:05.123456+00:00",
    "updatedAt": "2020-02-03T04:05:06.123456+00:00",
    "favorited": True,
    "favoritesCount": 123,
    "author": {
        "username": "test-2",
        "bio": "test bio",
        "image": "https://test.test/image.jpg",
        "following": True,
    },
}
