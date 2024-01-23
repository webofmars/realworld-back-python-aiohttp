__all__ = [
    "UseCase",
]

import abc
import typing as t

T = t.TypeVar("T", contravariant=True)
R = t.TypeVar("R", covariant=True)


class UseCase(t.Protocol[T, R]):
    @abc.abstractmethod
    async def execute(self, input: T, /) -> R:
        raise NotImplementedError()
