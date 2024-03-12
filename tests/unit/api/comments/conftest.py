__all__ = [
    "COMMENT_1",
    "COMMENT_2",
    "EXPECTED_SERIALIZED_COMMENT_1",
    "EXPECTED_SERIALIZED_COMMENT_2",
]
import datetime as dt

from yarl import URL

from conduit.core.entities.article import ArticleId
from conduit.core.entities.comment import Comment, CommentId, CommentWithExtra
from conduit.core.entities.user import Email, PasswordHash, User, UserId, Username

COMMENT_1 = CommentWithExtra(
    v=Comment(
        id=CommentId(1),
        author_id=UserId(101),
        article_id=ArticleId(2),
        created_at=dt.datetime(2020, 1, 2, 3, 4, 5, 123456),
        updated_at=None,
        body="comment-1",
    ),
    author=User(
        id=UserId(101),
        username=Username("test"),
        email=Email("test@test.test"),
        password=PasswordHash("test"),
        bio="",
        image=None,
    ),
    is_author_followed=False,
)
COMMENT_2 = CommentWithExtra(
    v=Comment(
        id=CommentId(2),
        author_id=UserId(202),
        article_id=ArticleId(3),
        created_at=dt.datetime(2020, 1, 2, 3, 4, 5, 123456),
        updated_at=dt.datetime(2020, 2, 3, 4, 5, 6, 123456),
        body="comment-2",
    ),
    author=User(
        id=UserId(202),
        username=Username("test-2"),
        email=Email("test@test.test"),
        password=PasswordHash("test"),
        bio="test bio",
        image=URL("https://test.test/image.jpg"),
    ),
    is_author_followed=True,
)

EXPECTED_SERIALIZED_COMMENT_1 = {
    "id": 1,
    "createdAt": "2020-01-02T03:04:05.123456+00:00",
    "updatedAt": "2020-01-02T03:04:05.123456+00:00",
    "body": "comment-1",
    "author": {
        "username": "test",
        "bio": "",
        "image": None,
        "following": False,
    },
}
EXPECTED_SERIALIZED_COMMENT_2 = {
    "id": 2,
    "createdAt": "2020-01-02T03:04:05.123456+00:00",
    "updatedAt": "2020-02-03T04:05:06.123456+00:00",
    "body": "comment-2",
    "author": {
        "username": "test-2",
        "bio": "test bio",
        "image": "https://test.test/image.jpg",
        "following": True,
    },
}
