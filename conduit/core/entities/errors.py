__all__ = [
    "ArticleDoesNotExistError",
    "ConduitError",
    "EmailAlreadyExistsError",
    "InvalidCredentialsError",
    "PermissionDeniedError",
    "UserIsNotAuthenticatedError",
    "UsernameAlreadyExistsError",
    "Visitor",
]

import abc
import typing as t

T_co = t.TypeVar("T_co", covariant=True)


class ConduitError(abc.ABC, Exception):
    @abc.abstractmethod
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        raise NotImplementedError()


class UsernameAlreadyExistsError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_username_already_exists(self)


class EmailAlreadyExistsError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_email_already_exists(self)


class InvalidCredentialsError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_invalid_credentials(self)


class UserIsNotAuthenticatedError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_user_is_not_authenticated(self)


class PermissionDeniedError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_permission_denied(self)


class ArticleDoesNotExistError(ConduitError):
    def accept(self, visitor: "Visitor[T_co]") -> T_co:
        return visitor.visit_article_does_not_exist(self)


class Visitor(t.Protocol[T_co]):
    @abc.abstractmethod
    def visit_username_already_exists(self, error: UsernameAlreadyExistsError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_email_already_exists(self, error: EmailAlreadyExistsError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_invalid_credentials(self, error: InvalidCredentialsError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_user_is_not_authenticated(self, error: UserIsNotAuthenticatedError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_permission_denied(self, error: PermissionDeniedError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_article_does_not_exist(self, error: ArticleDoesNotExistError) -> T_co:
        raise NotImplementedError()
