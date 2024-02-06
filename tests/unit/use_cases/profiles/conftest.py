import pytest

from conduit.core.entities.user import Email, PasswordHash, User, UserId, Username


@pytest.fixture
def follower() -> User:
    return User(
        id=UserId(123),
        username=Username("follower"),
        email=Email("follower@test.test"),
        password=PasswordHash("test"),
        bio="",
        image=None,
    )
