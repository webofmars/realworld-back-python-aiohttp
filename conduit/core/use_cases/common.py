__all__ = [
    "are_users_followed",
    "get_article",
    "get_users",
    "is_user_followed",
]

import logging
import typing as t

from conduit.core.entities.article import Article, ArticleSlug
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId

LOG = logging.getLogger(__name__)


async def get_article(unit_of_work: UnitOfWork, slug: ArticleSlug) -> Article | None:
    async with unit_of_work.begin() as uow:
        article = await uow.articles.get_by_slug(slug)
    if article is None:
        LOG.info("article not found", extra={"slug": slug})
        return None
    LOG.info("got article", extra={"slug": slug, "article_id": article.id})
    return article


async def get_users(unit_of_work: UnitOfWork, ids: t.Collection[UserId]) -> t.Mapping[UserId, User]:
    async with unit_of_work.begin() as uow:
        users = await uow.users.get_by_ids(ids)
    LOG.info("got users", extra={"ids": ids, "user_ids": list(users)})
    return users


async def is_user_followed(unit_of_work: UnitOfWork, id: UserId, *, by: UserId | None) -> bool:
    if by is None:
        LOG.info("user is not authenticated, not followed")
        return False
    async with unit_of_work.begin() as uow:
        is_followed = await uow.followers.is_followed(id, by=by)
    LOG.info(
        "got following status",
        extra={"id": id, "by": by, "is_followed": is_followed},
    )
    return is_followed


async def are_users_followed(
    unit_of_work: UnitOfWork,
    user_ids: t.Collection[UserId],
    by: UserId | None,
) -> t.Mapping[UserId, bool]:
    if by is None:
        LOG.info("user is not authenticated, not followed")
        return {}
    async with unit_of_work.begin() as uow:
        are_followed = await uow.followers.are_followed(user_ids, by)
    LOG.info(
        "got following status",
        extra={"user_ids": user_ids, "by": by, "are_followed": are_followed},
    )
    return are_followed
