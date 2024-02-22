__all__ = [
    "UnitOfWork",
    "UnitOfWorkContext",
]
import abc
import typing as t

from conduit.core.entities.article import ArticleRepository, FavoriteRepository, TagRepository
from conduit.core.entities.comment import CommentRepository
from conduit.core.entities.user import FollowerRepository, UserRepository

T = t.TypeVar("T")


class UnitOfWorkContext(t.Protocol):
    @property
    @abc.abstractmethod
    def users(self) -> UserRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def followers(self) -> FollowerRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def articles(self) -> ArticleRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def tags(self) -> TagRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def favorites(self) -> FavoriteRepository:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def comments(self) -> CommentRepository:
        raise NotImplementedError()


class UnitOfWork(t.Protocol):
    """Abstraction over the idea of atomic operations."""

    @abc.abstractmethod
    def begin(self) -> t.AsyncContextManager[UnitOfWorkContext]:
        raise NotImplementedError()
