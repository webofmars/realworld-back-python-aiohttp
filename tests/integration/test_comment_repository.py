import datetime as dt

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.article import Article
from conduit.core.entities.comment import CommentFilter, CommentId, CreateCommentInput
from conduit.core.entities.user import User
from conduit.impl.comment_repository import PostgresqlCommentRepository


@pytest.mark.parametrize(
    "author_ix, article_ix, body",
    [
        (0, 0, "t1"),
        (1, 0, "t2"),
        (1, 1, "t3"),
    ],
)
async def test_create(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
    author_ix: int,
    article_ix: int,
    body: str,
) -> None:
    # Arrange
    author = existing_users[author_ix]
    article = existing_articles[article_ix]

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        comment = await repo.create(CreateCommentInput(author.id, article.id, body))

    # Assert
    assert isinstance(comment.id, int)
    assert comment.author_id == author.id
    assert comment.article_id == article.id
    assert comment.body == body
    assert isinstance(comment.created_at, dt.datetime)
    assert comment.updated_at is None


async def test_get_many(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        await repo.create(CreateCommentInput(user.id, article.id, "t1"))
        await repo.create(CreateCommentInput(other_user.id, article.id, "t2"))
        await repo.create(CreateCommentInput(other_user.id, other_article.id, "t3"))

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        comments_1 = await repo.get_many(CommentFilter(article.id))
        comments_2 = await repo.get_many(CommentFilter(other_article.id))

    # Assert
    assert len(comments_1) == 2
    assert comments_1[0].author_id == user.id
    assert comments_1[0].body == "t1"
    assert comments_1[1].author_id == other_user.id
    assert comments_1[1].body == "t2"
    assert len(comments_2) == 1
    assert comments_2[0].author_id == other_user.id
    assert comments_2[0].body == "t3"


async def test_get_by_id(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        expected_comment_1 = await repo.create(CreateCommentInput(user.id, article.id, "t1"))
        expected_comment_2 = await repo.create(CreateCommentInput(other_user.id, other_article.id, "t3"))

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        comment_1 = await repo.get_by_id(expected_comment_1.id)
        comment_2 = await repo.get_by_id(expected_comment_2.id)
        comment_3 = await repo.get_by_id(CommentId(123456))

    # Assert
    assert comment_1 is not None
    assert comment_1 == expected_comment_1
    assert comment_2 is not None
    assert comment_2 == expected_comment_2
    assert comment_3 is None


async def test_delete(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        expected_comment_1 = await repo.create(CreateCommentInput(user.id, article.id, "t1"))
        expected_comment_2 = await repo.create(CreateCommentInput(other_user.id, other_article.id, "t3"))

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlCommentRepository(connection)
        comment_id_1 = await repo.delete(expected_comment_1.id)
        comment_id_2 = await repo.delete(expected_comment_2.id)
        comment_id_3 = await repo.delete(CommentId(123456))

    # Assert
    assert comment_id_1 is not None
    assert comment_id_1 == expected_comment_1.id
    assert comment_id_2 is not None
    assert comment_id_2 == expected_comment_2.id
    assert comment_id_3 is None
