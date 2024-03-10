__all__ = [
    "are_favorite",
    "get_article_count",
    "get_articles",
    "get_author",
    "get_favorite_count_for_article",
    "get_favorite_count_for_articles",
    "get_tags_for_article",
    "get_tags_for_articles",
    "is_favorite",
]

import typing as t

import structlog

from conduit.core.entities.article import Article, ArticleFilter, ArticleId, Tag
from conduit.core.entities.unit_of_work import UnitOfWork
from conduit.core.entities.user import User, UserId

LOG = structlog.get_logger(__name__)


async def get_articles(unit_of_work: UnitOfWork, filter: ArticleFilter, *, limit: int, offset: int) -> list[Article]:
    async with unit_of_work.begin() as uow:
        articles = await uow.articles.get_many(filter, limit=limit, offset=offset)
    LOG.info("got articles", filter=filter, article_ids=[article.id for article in articles])
    return articles


async def get_article_count(unit_of_work: UnitOfWork, filter: ArticleFilter) -> int:
    async with unit_of_work.begin() as uow:
        count = await uow.articles.count(filter)
    LOG.info("got article count", filter=filter, count=count)
    return count


async def get_author(unit_of_work: UnitOfWork, author_id: UserId) -> User:
    async with unit_of_work.begin() as uow:
        author = await uow.users.get_by_id(author_id)
        assert author is not None, "article author must exist"
    LOG.info("got article author", author_id=author_id)
    return author


async def get_tags_for_article(unit_of_work: UnitOfWork, article_id: ArticleId) -> list[Tag]:
    async with unit_of_work.begin() as uow:
        tags = await uow.tags.get_for_article(article_id)
    LOG.info("got article tags", article_id=article_id, tags=tags)
    return tags


async def get_tags_for_articles(
    unit_of_work: UnitOfWork,
    article_ids: t.Collection[ArticleId],
) -> t.Mapping[ArticleId, list[Tag]]:
    async with unit_of_work.begin() as uow:
        tags = await uow.tags.get_for_articles(article_ids)
    LOG.info("got articles tags", article_ids=article_ids)
    return tags


async def is_favorite(unit_of_work: UnitOfWork, article_id: ArticleId, of: UserId | None) -> bool:
    if of is None:
        LOG.info("user is not authenticated, article is not in the favorites")
        return False
    async with unit_of_work.begin() as uow:
        is_favorite = await uow.favorites.is_favorite(article_id, of)
    LOG.info("got article favorite status", user_id=of, article_id=article_id, is_favorite=is_favorite)
    return is_favorite


async def are_favorite(
    unit_of_work: UnitOfWork,
    article_ids: t.Collection[ArticleId],
    of: UserId | None,
) -> t.Mapping[ArticleId, bool]:
    if of is None:
        LOG.info("user is not authenticated, articles are not in the favorites")
        return {}
    async with unit_of_work.begin() as uow:
        are_favorite = await uow.favorites.are_favorite(article_ids, of)
    LOG.info("got articles favorite status", user_id=of, article_ids=article_ids, are_favorite=are_favorite)
    return are_favorite


async def get_favorite_count_for_article(unit_of_work: UnitOfWork, article_id: ArticleId) -> int:
    async with unit_of_work.begin() as uow:
        count = await uow.favorites.count(article_id)
    LOG.info("get favorite count for article", article_id=article_id, count=count)
    return count


async def get_favorite_count_for_articles(
    unit_of_work: UnitOfWork,
    article_ids: t.Collection[ArticleId],
) -> t.Mapping[ArticleId, int]:
    async with unit_of_work.begin() as uow:
        count = await uow.favorites.count_many(article_ids)
    LOG.info("get favorite count for articles", article_ids=article_ids, count=count)
    return count
