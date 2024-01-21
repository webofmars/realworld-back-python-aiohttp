__all__ = [
    "ConduitError",
    "EmailAlreadyExistsError",
    "UsernameAlreadyExistsError",
    "Visitor",
]

import abc
import typing as t


T = t.TypeVar("T")


class ConduitError(abc.ABC, Exception):
    @abc.abstractmethod
    def accept(self, visitor: "Visitor[T]") -> T:
        raise NotImplementedError()


class UsernameAlreadyExistsError(ConduitError):
    def accept(self, visitor: "Visitor[T]") -> T:
        return visitor.visit_username_already_exists(self)


class EmailAlreadyExistsError(ConduitError):
    def accept(self, visitor: "Visitor[T]") -> T:
        return visitor.visit_email_already_exists(self)


class Visitor(t.Protocol[T]):
    @abc.abstractmethod
    def visit_username_already_exists(self, error: UsernameAlreadyExistsError) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_email_already_exists(self, error: EmailAlreadyExistsError) -> T:
        raise NotImplementedError()
