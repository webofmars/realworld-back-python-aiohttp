__all__ = [
    "REQUEST_ID_VAR",
    "logging_middleware",
    "request_id_middleware",
]

import contextvars
import time
import typing as t
import uuid
from http import HTTPStatus

import structlog
from aiohttp import web

LOG = structlog.get_logger(__name__)
REQUEST_ID_VAR: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")


@web.middleware
async def request_id_middleware(
    request: web.Request,
    handler: t.Callable[[web.Request], t.Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    REQUEST_ID_VAR.set(uuid.uuid4().hex)
    return await handler(request)


@web.middleware
async def logging_middleware(
    request: web.Request,
    handler: t.Callable[[web.Request], t.Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    log = LOG.bind(path=request.path, method=request.method, query=request.query_string)
    log.info("handling HTTP request")
    t0 = time.perf_counter()
    try:
        response = await handler(request)
    except Exception:
        log.exception("unexpected error")
        response = web.json_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
    finally:
        log.info(
            "HTTP request processed",
            status=response.status,
            duration=round(time.perf_counter() - t0, 3),
        )
    return response
