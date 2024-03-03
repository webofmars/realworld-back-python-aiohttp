__all__ = [
    "USER_NOT_FOUND_RESPONSE",
]

import typing as t
from http import HTTPStatus

from aiohttp import web

USER_NOT_FOUND_RESPONSE: t.Final = web.json_response({"error": "user not found"}, status=HTTPStatus.NOT_FOUND)
