import datetime as dt
from dataclasses import replace

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.article import Article, ArticleFilter, ArticleId, ArticleSlug, CreateArticleInput
from conduit.core.entities.user import User, UserId
from conduit.impl.article_repository import PostgresqlArticleRepository


@pytest.fixture
async def existing_articles(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> list[Article]:
    user_1, user_2 = existing_users
    create_inputs = [
        CreateArticleInput(user_1.id, "title-1", "description-1", "body-1"),
        CreateArticleInput(user_1.id, "title-2", "description-2", "body-2"),
        CreateArticleInput(user_2.id, "title-3", "description-3", "body-3"),
        CreateArticleInput(user_2.id, "title-4", "description-4", "body-4"),
    ]
    articles = []
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        for input in create_inputs:
            article = await repo.create(input)
            articles.append(article)
    return articles


@pytest.mark.parametrize(
    "input, author_ix",
    [
        (CreateArticleInput(UserId(0), "test title 1", "test description 1", "test body 1"), 0),
        (CreateArticleInput(UserId(0), "test title 2", "test description 2", "test body 2"), 1),
    ],
)
async def test_create(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    input: CreateArticleInput,
    author_ix: int,
) -> None:
    # Arrange
    author_id = existing_users[author_ix].id
    input = replace(input, author_id=author_id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        article = await repo.create(input)

    # Assert
    assert article.author_id == input.author_id
    assert article.title == input.title
    assert article.description == input.description
    assert article.body == input.body
    assert isinstance(article.created_at, dt.datetime)
    assert article.updated_at is None


@pytest.mark.parametrize("article_ix", [0, 2])
async def test_get_by_slug(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    article_ix: int,
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        article = await repo.get_by_slug(existing_articles[article_ix].slug)

    # Assert
    assert article is not None
    assert article == existing_articles[article_ix]


async def test_get_by_slug_not_existing(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        article = await repo.get_by_slug(ArticleSlug("not-existing-article"))

    # Assert
    assert article is None


@pytest.mark.parametrize("article_ix", [1, 3])
async def test_delete(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    article_ix: int,
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        deleted_article_id = await repo.delete(existing_articles[article_ix].id)

    # Assert
    assert deleted_article_id is not None
    assert deleted_article_id == existing_articles[article_ix].id
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        count_after_delete = await repo.count(ArticleFilter())
    assert count_after_delete == len(existing_articles) - 1


async def test_delete_not_existing(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        deleted_article_id = await repo.delete(ArticleId(123456))

    # Assert
    assert deleted_article_id is None
    async with db_engine.begin() as connection:
        repo = PostgresqlArticleRepository(connection)
        count_after_delete = await repo.count(ArticleFilter())
    assert count_after_delete == len(existing_articles)
