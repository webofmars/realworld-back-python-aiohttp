__all__ = [
    "ErrorModel",
    "ErrorSchema",
    "ProfileModel",
    "ProfileSchema",
    "UserModel",
    "UserSchema",
]

from dataclasses import dataclass

from marshmallow import Schema, fields

from conduit.core.entities.user import User, AuthToken


@dataclass(frozen=True)
class ErrorModel:
    error: str


class ErrorSchema(Schema):
    error = fields.String(required=True)


@dataclass(frozen=True)
class UserModel:
    token: str
    email: str
    username: str
    bio: str
    image: str | None

    @classmethod
    def new(cls, user: User, token: AuthToken) -> "UserModel":
        return UserModel(
            token=token,
            email=user.email,
            username=user.username,
            bio=user.bio,
            image=str(user.image) if user.image is not None else None,
        )


class UserSchema(Schema):
    token = fields.String(required=True)
    email = fields.Email(required=True)
    username = fields.String(required=True)
    bio = fields.String(required=True)
    image = fields.URL(required=False, allow_none=True)


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
