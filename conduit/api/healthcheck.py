__all__ = [
    "healthcheck",
]

from aiohttp import web


async def healthcheck(_: web.Request) -> web.Response:
    return web.json_response({"ok": True})
