import pytest

from conduit.core.entities.user import RawPassword
from conduit.impl.password_hasher import Argon2idPasswordHasher


@pytest.mark.parametrize(
    "hasher_params, hash_password, verify_password, expected_result",
    [
        pytest.param(
            (19456, 2, 1),
            "test",
            "test",
            True,
            id="1",
        ),
        pytest.param(
            (47104, 1, 4),
            "test-test-test",
            "test-test-test",
            True,
            id="2",
        ),
        pytest.param(
            (19456, 2, 1),
            "test-1",
            "test-2",
            False,
            id="3",
        ),
        pytest.param(
            (19456, 2, 1),
            "test-10",
            "test-1",
            False,
            id="4",
        ),
    ],
)
async def test_password_hasher(
    hasher_params: tuple[int, int, int],
    hash_password: str,
    verify_password: str,
    expected_result: bool,
) -> None:
    # Arrange
    hasher = Argon2idPasswordHasher(*hasher_params)
    hash = await hasher.hash_password(RawPassword(hash_password))

    # Act
    hasher = Argon2idPasswordHasher()
    result = await hasher.verify(RawPassword(verify_password), hash)

    # Assert
    assert result is expected_result
