__all__ = [
    "Tag",
    "TagRepository",
]

import abc
import typing as t
from dataclasses import dataclass


@dataclass(frozen=True)
class Tag:
    v: str


class TagRepository(t.Protocol):
    @abc.abstractmethod
    async def get_all(self) -> list[Tag]:
        raise NotImplementedError()
