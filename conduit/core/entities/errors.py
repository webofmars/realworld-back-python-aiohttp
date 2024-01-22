__all__ = [
    "ConduitError",
    "EmailAlreadyExistsError",
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


class Visitor(t.Protocol[T_co]):
    @abc.abstractmethod
    def visit_username_already_exists(self, error: UsernameAlreadyExistsError) -> T_co:
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_email_already_exists(self, error: EmailAlreadyExistsError) -> T_co:
        raise NotImplementedError()
