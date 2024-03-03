__all__ = [
    "Endpoint",
]

import typing as t

from aiohttp import web


Endpoint = t.Callable[[web.Request], t.Awaitable[web.Response]]
