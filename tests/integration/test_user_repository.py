import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from yarl import URL

from conduit.core.entities.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from conduit.core.entities.user import CreateUserInput, Email, PasswordHash, UpdateUserInput, User, UserId, Username
from conduit.impl.user_repository import PostgresqlUserRepository


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(
            CreateUserInput(
                username=Username("test-1"),
                email=Email("test-1@test.test"),
                password=PasswordHash("test-password-hash-1"),
            ),
            id="1",
        ),
        pytest.param(
            CreateUserInput(
                username=Username("test-2"),
                email=Email("test-2@test.test"),
                password=PasswordHash("test-password-hash-2"),
            ),
            id="2",
        ),
    ],
)
async def test_create(db_engine: AsyncEngine, input: CreateUserInput) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        user = await repo.create(input)

    # Assert
    assert isinstance(user.id, int)
    assert user.username == input.username
    assert user.email == input.email
    assert user.password == input.password
    assert user.bio == ""
    assert user.image is None


async def test_create_username_already_exists(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Arrange
    user, _ = existing_users

    # Act
    with pytest.raises(UsernameAlreadyExistsError):
        async with db_engine.begin() as connection:
            repo = PostgresqlUserRepository(connection)
            await repo.create(
                CreateUserInput(
                    username=user.username,
                    email=Email("foo@test.test"),
                    password=PasswordHash("test"),
                )
            )

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert await repo.get_by_email(Email("foo@test.test")) is None


async def test_create_email_already_exists(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Arrange
    _, user = existing_users

    # Act
    with pytest.raises(EmailAlreadyExistsError):
        async with db_engine.begin() as connection:
            repo = PostgresqlUserRepository(connection)
            await repo.create(
                CreateUserInput(
                    username=Username("foobar-test"),
                    email=user.email,
                    password=PasswordHash("test"),
                )
            )

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert await repo.get_by_email(user.email) == user


async def test_get_by_email(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    expected_user_1, expected_user_2 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        actual_user_1 = await repo.get_by_email(expected_user_1.email)
        actual_user_2 = await repo.get_by_email(expected_user_2.email)

    # Assert
    assert actual_user_1 == expected_user_1
    assert actual_user_2 == expected_user_2


@pytest.mark.parametrize("email", ["test-3@test.test", "test-4@test.test"])
async def test_get_by_email_not_found(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    email: Email,
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        user = await repo.get_by_email(email)

    # Assert
    assert user is None


async def test_get_username(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    expected_user_1, expected_user_2 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        actual_user_1 = await repo.get_by_username(expected_user_1.username)
        actual_user_2 = await repo.get_by_username(expected_user_2.username)

    # Assert
    assert actual_user_1 == expected_user_1
    assert actual_user_2 == expected_user_2


@pytest.mark.parametrize("username", ["foo", "bar"])
async def test_get_by_username_not_found(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    username: Username,
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        user = await repo.get_by_username(username)

    # Assert
    assert user is None


async def test_get_by_id(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    expected_user_1, expected_user_2 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        actual_user_1 = await repo.get_by_id(expected_user_1.id)
        actual_user_2 = await repo.get_by_id(expected_user_2.id)

    # Assert
    assert actual_user_1 == expected_user_1
    assert actual_user_2 == expected_user_2


@pytest.mark.parametrize("id", [1234, 4321])
async def test_get_by_id_not_found(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    id: UserId,
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        user = await repo.get_by_id(id)

    # Assert
    assert user is None


async def test_get_by_ids(db_engine: AsyncEngine, existing_users: tuple[User, User]) -> None:
    # Arrange
    expected_user_1, expected_user_2 = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        users = await repo.get_by_ids([expected_user_1.id, UserId(123456), expected_user_2.id])

    # Assert
    assert len(users) == 2
    assert users[expected_user_1.id] == expected_user_1
    assert users[expected_user_2.id] == expected_user_2


@pytest.mark.parametrize(
    "input, expected_attrs",
    [
        pytest.param(
            UpdateUserInput(),
            [
                ("username", "test-1"),
                ("email", "test-1@test.test"),
                ("password", "test-1"),
                ("bio", ""),
                ("image", None),
            ],
            id="1",
        ),
        pytest.param(
            UpdateUserInput(username=Username("foo")),
            [
                ("username", "foo"),
                ("email", "test-1@test.test"),
                ("password", "test-1"),
                ("bio", ""),
                ("image", None),
            ],
            id="2",
        ),
        pytest.param(
            UpdateUserInput(username=Username("bar"), email=Email("test-10@test.test")),
            [
                ("username", "bar"),
                ("email", "test-10@test.test"),
                ("password", "test-1"),
                ("bio", ""),
                ("image", None),
            ],
            id="3",
        ),
        pytest.param(
            UpdateUserInput(bio="test", image=URL("https://test.test/test.jpg")),
            [
                ("username", "test-1"),
                ("email", "test-1@test.test"),
                ("password", "test-1"),
                ("bio", "test"),
                ("image", URL("https://test.test/test.jpg")),
            ],
            id="4",
        ),
        pytest.param(
            UpdateUserInput(password=PasswordHash("test-10"), email=Email("test-10@test.test")),
            [
                ("username", "test-1"),
                ("email", "test-10@test.test"),
                ("password", "test-10"),
                ("bio", ""),
                ("image", None),
            ],
            id="5",
        ),
    ],
)
async def test_update(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
    input: UpdateUserInput,
    expected_attrs: list[tuple[str, object]],
) -> None:
    # Arrange
    user_to_update, _ = existing_users

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        updated_user = await repo.update(user_to_update.id, input)

    # Assert
    assert updated_user is not None
    for attr, expected_value in expected_attrs:
        assert getattr(updated_user, attr) == expected_value, attr
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert await repo.get_by_id(user_to_update.id) == updated_user


async def test_update_other_user_is_not_updated(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Arrange
    other_user, user_to_update = existing_users

    # Act
    input = UpdateUserInput(
        username=Username("foo"),
        email=Email("bar@test.test"),
        password=PasswordHash("new-password"),
        bio="test",
        image=URL("https://test.test/test.jpg"),
    )
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        updated_user = await repo.update(user_to_update.id, input)

    # Assert
    assert updated_user is not None
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert updated_user == await repo.get_by_id(user_to_update.id)
        assert other_user == await repo.get_by_id(other_user.id)


async def test_update_user_not_found(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Act
    input = UpdateUserInput(
        username=Username("foo"),
        email=Email("bar@test.test"),
        password=PasswordHash("new-password"),
        bio="test",
        image=URL("https://test.test/test.jpg"),
    )
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        updated_user = await repo.update(UserId(123456), input)

    # Assert
    assert updated_user is None


async def test_update_username_already_exists(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Arrange
    user_to_update, other_user = existing_users

    # Act
    with pytest.raises(UsernameAlreadyExistsError):
        async with db_engine.begin() as connection:
            repo = PostgresqlUserRepository(connection)
            await repo.update(
                user_to_update.id,
                UpdateUserInput(
                    username=other_user.username,
                    bio="test",
                ),
            )

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert await repo.get_by_id(user_to_update.id) == user_to_update


async def test_update_email_already_exists(
    db_engine: AsyncEngine,
    existing_users: tuple[User, User],
) -> None:
    # Arrange
    other_user, user_to_update = existing_users

    # Act
    with pytest.raises(EmailAlreadyExistsError):
        async with db_engine.begin() as connection:
            repo = PostgresqlUserRepository(connection)
            await repo.update(
                user_to_update.id,
                UpdateUserInput(
                    email=other_user.email,
                    password=PasswordHash("test"),
                ),
            )

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlUserRepository(connection)
        assert await repo.get_by_id(user_to_update.id) == user_to_update
