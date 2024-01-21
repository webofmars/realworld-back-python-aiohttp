__all__ = [
    "UseCase",
]

import abc
import typing as t

T = t.TypeVar("T", contravariant=True)
S = t.TypeVar("S", covariant=True)


class UseCase(t.Protocol[T, S]):
    @abc.abstractmethod
    async def execute(self, input: T, /) -> S:
        raise NotImplementedError()
