__all__ = [
    "ErrorModel",
    "ErrorSchema",
    "ProfileModel",
    "ProfileSchema",
]

from dataclasses import dataclass

from marshmallow import Schema, fields

from conduit.core.entities.user import User


@dataclass(frozen=True)
class ErrorModel:
    error: str


class ErrorSchema(Schema):
    error = fields.String(required=True)


@dataclass(frozen=True)
class ProfileModel:
    username: str
    bio: str
    image: str | None
    following: bool

    @classmethod
    def new(cls, user: User, following: bool) -> "ProfileModel":
        return ProfileModel(
            username=user.username,
            bio=user.bio,
            image=str(user.image) if user.image is not None else None,
            following=following,
        )


class ProfileSchema(Schema):
    username = fields.String(required=True)
    bio = fields.String(required=True)
    image = fields.URL(required=False, allow_none=True)
    following = fields.Boolean(required=True)
