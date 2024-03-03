__all__ = [
    "convert_to_user_response",
]

from http import HTTPStatus

from aiohttp import web

from conduit.core.entities.user import AuthToken, User


def convert_to_user_response(user: User, token: AuthToken, status: HTTPStatus = HTTPStatus.OK) -> web.Response:
    return web.json_response(
        {
            "user": {
                "token": token,
                "email": user.email,
                "username": user.username,
                "bio": user.bio,
                "image": str(user.image) if user.image is not None else None,
            }
        },
        status=status,
    )
