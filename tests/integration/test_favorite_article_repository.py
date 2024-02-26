from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.article import Article
from conduit.core.entities.user import User
from conduit.impl.favorite_article_repository import PostgresqlFavoriteArticleRepository


async def test_add_to_favorites(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_ = existing_articles

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        favorite_count_1 = await repo.add(user.id, article.id)
        favorite_count_2 = await repo.add(user.id, article.id)
        favorite_count_3 = await repo.add(other_user.id, article.id)

    # Assert
    assert favorite_count_1 == 1
    assert favorite_count_2 == 1
    assert favorite_count_3 == 2


async def test_remove_from_favorites(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        await repo.add(user.id, article.id)
        await repo.add(other_user.id, article.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        favorite_count_1 = await repo.remove(user.id, article.id)
        favorite_count_2 = await repo.remove(other_user.id, article.id)
        favorite_count_3 = await repo.remove(other_user.id, other_article.id)

    # Assert
    assert favorite_count_1 == 1
    assert favorite_count_2 == 0
    assert favorite_count_3 == 0


async def test_is_favorite(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        await repo.add(user.id, article.id)
        await repo.add(other_user.id, article.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        is_favorite_1 = await repo.is_favorite(article.id, user.id)
        is_favorite_2 = await repo.is_favorite(article.id, other_user.id)
        is_favorite_3 = await repo.is_favorite(other_article.id, other_user.id)

    # Assert
    assert is_favorite_1
    assert is_favorite_2
    assert not is_favorite_3


async def test_are_favorite(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        await repo.add(user.id, article.id)
        await repo.add(user.id, other_article.id)
        await repo.add(other_user.id, article.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        article_ids = [article.id for article in existing_articles]
        are_favorite_of_user = await repo.are_favorite(article_ids, user.id)
        are_favorite_of_other_user = await repo.are_favorite(article_ids, other_user.id)

    # Assert
    assert are_favorite_of_user == {article.id: True, other_article.id: True}
    assert are_favorite_of_other_user == {article.id: True}


async def test_count(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        await repo.add(user.id, article.id)
        await repo.add(user.id, other_article.id)
        await repo.add(other_user.id, article.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        count_1 = await repo.count(article.id)
        count_2 = await repo.count(other_article.id)

    # Assert
    assert count_1 == 2
    assert count_2 == 1


async def test_count_many(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    existing_articles: list[Article],
) -> None:
    # Arrange
    user, other_user = existing_users
    article, *_, other_article = existing_articles
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        await repo.add(user.id, article.id)
        await repo.add(user.id, other_article.id)
        await repo.add(other_user.id, article.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFavoriteArticleRepository(connection)
        article_ids = [article.id for article in existing_articles]
        count = await repo.count_many(article_ids)

    # Assert
    assert count == {article.id: 2, other_article.id: 1}
