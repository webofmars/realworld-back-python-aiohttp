import datetime as dt

import pytest

from conduit.core.entities.user import AuthToken, Email, PasswordHash, User, UserId, Username
from conduit.impl.auth_token_generator import JwtAuthTokenGenerator


@pytest.fixture
def user_id() -> UserId:
    return UserId(1)


@pytest.fixture
def user(user_id: UserId) -> User:
    return User(
        id=user_id,
        username=Username("test"),
        email=Email("test@test.test"),
        password=PasswordHash("test"),
        bio="",
        image=None,
    )


@pytest.mark.parametrize(
    [
        "token_generated_with_secret",
        "token_generated_at",
        "expiration_time",
        "user_id",
        "token_decoded_with_secret",
        "expected_user_id",
    ],
    [
        pytest.param(
            "test-1",
            dt.datetime.utcnow() - dt.timedelta(hours=23),
            dt.timedelta(hours=24),
            UserId(123),
            "test-1",
            UserId(123),
            id="1",
        ),
        pytest.param(
            "test-2",
            dt.datetime.utcnow() - dt.timedelta(hours=47),
            dt.timedelta(hours=48),
            UserId(321),
            "test-2",
            UserId(321),
            id="2",
        ),
        pytest.param(
            "test-3",
            dt.datetime.utcnow() - dt.timedelta(hours=49),
            dt.timedelta(hours=48),
            UserId(321),
            "test-3",
            None,
            id="3-expired",
        ),
        pytest.param(
            "test-4",
            dt.datetime.utcnow() - dt.timedelta(hours=47),
            dt.timedelta(hours=48),
            UserId(321),
            "test-40",
            None,
            id="4-invalid-secret",
        ),
    ],
)
async def test_auth_token_generator(
    user: User,
    token_generated_with_secret: str,
    token_generated_at: dt.datetime,
    expiration_time: dt.timedelta,
    user_id: UserId,
    token_decoded_with_secret: str,
    expected_user_id: UserId | None,
) -> None:
    # Arrange
    generator = JwtAuthTokenGenerator(
        secret_key=token_generated_with_secret,
        expiration_time=expiration_time,
        now=lambda: token_generated_at,
    )
    token = await generator.generate_token(user)

    # Act
    generator = JwtAuthTokenGenerator(
        secret_key=token_decoded_with_secret,
        expiration_time=expiration_time,
        now=lambda: token_generated_at,
    )
    decoded_user_id = await generator.get_user_id(token)

    # Assert
    assert decoded_user_id == expected_user_id


@pytest.mark.parametrize(
    "invalid_token",
    [
        AuthToken(""),
        AuthToken("test"),
        AuthToken("asdjaslkjdlkasjdkljasd.asdjlkasjdljasdhasjkhfskd.asdjkhsakfhsajkhdfkjs"),
    ],
)
async def test_invalid_token(invalid_token: AuthToken) -> None:
    # Act
    generator = JwtAuthTokenGenerator(secret_key="test", expiration_time=dt.timedelta(hours=48))
    user_id = await generator.get_user_id(invalid_token)

    # Assert
    assert user_id is None
