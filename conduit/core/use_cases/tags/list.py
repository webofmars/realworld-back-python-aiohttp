__all__ = [
    "ListTagsInput",
    "ListTagsResult",
    "ListTagsUseCase",
]

import logging
from dataclasses import dataclass

from conduit.core.entities.article import Tag
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.use_cases import UseCase

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class ListTagsInput:
    pass


@dataclass(frozen=True)
class ListTagsResult:
    tags: list[Tag]


class ListTagsUseCase(UseCase[ListTagsInput, ListTagsResult]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, input: ListTagsInput, /) -> ListTagsResult:
        async with self._unit_of_work.begin() as uow:
            tags = await uow.tags.get_all()
        return ListTagsResult(tags)
