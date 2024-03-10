__all__ = [
    "domain_error_handling_middleware",
]

import typing as t
from http import HTTPStatus

from aiohttp import web

from conduit.core.entities.errors import (
    ArticleDoesNotExistError,
    ConduitError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UserIsNotAuthenticatedError,
    UsernameAlreadyExistsError,
    Visitor,
)


@web.middleware
async def domain_error_handling_middleware(
    request: web.Request,
    handler: t.Callable[[web.Request], t.Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    try:
        return await handler(request)
    except ConduitError as err:
        response_body, response_status = err.accept(_HTTP_ERROR_VISITOR)
        return web.json_response(response_body, status=response_status)


class HttpErrorVisitor(Visitor[tuple[dict[str, t.Any], HTTPStatus]]):
    def visit_username_already_exists(
        self,
        error: UsernameAlreadyExistsError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "username already exists"}, HTTPStatus.BAD_REQUEST

    def visit_email_already_exists(
        self,
        error: EmailAlreadyExistsError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "email already exists"}, HTTPStatus.BAD_REQUEST

    def visit_invalid_credentials(
        self,
        error: InvalidCredentialsError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "invalid credentials"}, HTTPStatus.UNAUTHORIZED

    def visit_user_is_not_authenticated(
        self,
        error: UserIsNotAuthenticatedError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "user is not authenticated"}, HTTPStatus.UNAUTHORIZED

    def visit_permission_denied(
        self,
        error: PermissionDeniedError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "permission denied"}, HTTPStatus.FORBIDDEN

    def visit_article_does_not_exist(
        self,
        error: ArticleDoesNotExistError,
    ) -> tuple[dict[str, t.Any], HTTPStatus]:
        return {"error": "article not found"}, HTTPStatus.NOT_FOUND


_HTTP_ERROR_VISITOR = HttpErrorVisitor()
