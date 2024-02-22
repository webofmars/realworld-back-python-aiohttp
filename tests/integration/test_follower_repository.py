from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.user import User, UserId
from conduit.impl.follower_repository import PostgresqlFollowerRepository


async def test_follow(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_1, user_2 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_1.id, followed_id=user_2.id)

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        assert await repo.is_followed(user_2.id, by=user_1.id)
        assert not await repo.is_followed(user_1.id, by=user_2.id)


async def test_follow_is_idempotent(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_2, user_1 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_2.id, followed_id=user_1.id)
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_2.id, followed_id=user_1.id)

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        assert await repo.is_followed(user_1.id, by=user_2.id)
        assert not await repo.is_followed(user_2.id, by=user_1.id)


async def test_unfollow(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_1, user_2 = existing_users
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_1.id, followed_id=user_2.id)
        await repo.follow(follower_id=user_2.id, followed_id=user_1.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.unfollow(follower_id=user_1.id, followed_id=user_2.id)

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        assert not await repo.is_followed(user_2.id, by=user_1.id)
        assert await repo.is_followed(user_1.id, by=user_2.id)


async def test_unfollow_is_idempotent(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_1, user_2 = existing_users
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_1.id, followed_id=user_2.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.unfollow(follower_id=user_1.id, followed_id=user_2.id)
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.unfollow(follower_id=user_1.id, followed_id=user_2.id)

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        assert not await repo.is_followed(user_2.id, by=user_1.id)


async def test_is_followed(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_1, user_2 = existing_users
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_1.id, followed_id=user_2.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        user_1_follows_user_2 = await repo.is_followed(user_2.id, by=user_1.id)
        user_1_follows_user_3 = await repo.is_followed(UserId(3), by=user_1.id)
        user_2_follows_user_1 = await repo.is_followed(user_1.id, by=user_2.id)
        user_3_follows_user_1 = await repo.is_followed(user_1.id, by=UserId(3))

    # Assert
    assert user_1_follows_user_2
    assert not user_1_follows_user_3
    assert not user_2_follows_user_1
    assert not user_3_follows_user_1


async def test_are_followed(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    user_1, user_2 = existing_users
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        await repo.follow(follower_id=user_1.id, followed_id=user_1.id)
        await repo.follow(follower_id=user_1.id, followed_id=user_2.id)
        await repo.follow(follower_id=user_2.id, followed_id=user_1.id)

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlFollowerRepository(connection)
        user_1_followed_users = await repo.are_followed([user_1.id, user_2.id, UserId(123456)], by=user_1.id)
        user_2_followed_users = await repo.are_followed([user_1.id, user_2.id], by=user_2.id)
        user_3_followed_users = await repo.are_followed([], by=UserId(3))

    # Assert
    assert len(user_1_followed_users) == 3
    assert user_1_followed_users[user_1.id] is True
    assert user_1_followed_users[user_2.id] is True
    assert user_1_followed_users[UserId(123456)] is False
    assert len(user_2_followed_users) == 2
    assert user_2_followed_users[user_1.id] is True
    assert user_2_followed_users[user_2.id] is False
    assert len(user_3_followed_users) == 0
