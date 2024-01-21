__all__ = [
    "Profile",
]

from dataclasses import dataclass

from yarl import URL

from conduit.core.entities.common import Username


@dataclass(frozen=True)
class Profile:
    username: Username
    bio: str
    image: URL | None
    is_following: bool
