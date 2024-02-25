import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from conduit.core.entities.article import Article, Tag
from conduit.impl.tag_repository import PostgresqlTagRepository


@pytest.mark.parametrize(
    "tags, article_ix, expected_tags",
    [
        pytest.param([], 0, [], id="1"),
        pytest.param(["t1"], 1, ["t1"], id="2"),
        pytest.param(["t2", "t1"], 2, ["t2", "t1"], id="3"),
        pytest.param(["t2", "t1", "t2", "t1", "t3"], 3, ["t2", "t1", "t3"], id="4"),
    ],
)
async def test_create(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    tags: list[str],
    article_ix: int,
    expected_tags: list[str],
) -> None:
    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        await repo.create(article_id=existing_articles[article_ix].id, tags=[Tag(tag) for tag in tags])

    # Assert
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        actual_tags = await repo.get_for_article(existing_articles[article_ix].id)
    assert actual_tags == [Tag(tag) for tag in expected_tags]


@pytest.mark.parametrize(
    "tags, expected_tags",
    [
        pytest.param([], [], id="1"),
        pytest.param([("t1", 0)], ["t1"], id="2"),
        pytest.param([("t1", 0), ("t2", 0)], ["t1", "t2"], id="3"),
        pytest.param([("t1", 0), ("t2", 0), ("t1", 1), ("t1", 2)], ["t1", "t2"], id="4"),
        pytest.param([("t1", 0), ("t2", 0), ("t1", 1), ("t3", 2)], ["t1", "t2", "t3"], id="5"),
        pytest.param([("t4", 0), ("t3", 1), ("t2", 2), ("t1", 3)], ["t4", "t3", "t2", "t1"], id="6"),
    ],
)
async def test_get_all(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    tags: list[tuple[str, int]],
    expected_tags: list[str],
) -> None:
    # Arrange
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        for tag, article_ix in tags:
            await repo.create(existing_articles[article_ix].id, [Tag(tag)])

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        actual_tags = await repo.get_all()

    # Assert
    assert actual_tags == [Tag(tag) for tag in expected_tags]


@pytest.mark.parametrize(
    "tags, get_for_article_ix, expected_tags",
    [
        pytest.param([], 0, [], id="1"),
        pytest.param([("t1", 0)], 0, ["t1"], id="2"),
        pytest.param([("t1", 0)], 1, [], id="3"),
        pytest.param([("t1", 0), ("t2", 0)], 0, ["t1", "t2"], id="4"),
        pytest.param([("t1", 0), ("t2", 0), ("t1", 1), ("t1", 2)], 0, ["t1", "t2"], id="5"),
        pytest.param([("t1", 0), ("t2", 0), ("t1", 1), ("t1", 2)], 1, ["t1"], id="6"),
        pytest.param([("t1", 0), ("t2", 0), ("t1", 1), ("t2", 2)], 2, ["t2"], id="7"),
    ],
)
async def test_get_for_article(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    tags: list[tuple[str, int]],
    get_for_article_ix: int,
    expected_tags: list[str],
) -> None:
    # Arrange
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        for tag, article_ix in tags:
            await repo.create(existing_articles[article_ix].id, [Tag(tag)])

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        actual_tags = await repo.get_for_article(existing_articles[get_for_article_ix].id)

    # Assert
    assert actual_tags == [Tag(tag) for tag in expected_tags]


@pytest.mark.parametrize(
    "tags, get_for_article_ixs, expected_tags",
    [
        pytest.param([], [0], {0: []}, id="1"),
        pytest.param([("t1", 0)], [0, 1, 2], {0: ["t1"], 1: [], 2: []}, id="2"),
        pytest.param([("t1", 0)], [1], {1: []}, id="3"),
        pytest.param([("t1", 0), ("t2", 0)], [3, 0], {0: ["t1", "t2"], 3: []}, id="4"),
        pytest.param(
            [("t1", 0), ("t2", 0), ("t3", 1), ("t1", 2), ("t1", 1)],
            [0, 1, 2, 3],
            {0: ["t1", "t2"], 1: ["t1", "t3"], 2: ["t1"], 3: []},
            id="5",
        ),
    ],
)
async def test_get_for_articles(
    db_engine: AsyncEngine,
    existing_articles: list[Article],
    tags: list[tuple[str, int]],
    get_for_article_ixs: list[int],
    expected_tags: dict[int, list[str]],
) -> None:
    # Arrange
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        for tag, article_ix in tags:
            await repo.create(existing_articles[article_ix].id, [Tag(tag)])

    # Act
    async with db_engine.begin() as connection:
        repo = PostgresqlTagRepository(connection)
        actual_tags = await repo.get_for_articles([existing_articles[ix].id for ix in get_for_article_ixs])

    # Assert
    for expected_article_ix, expected_article_tags in expected_tags.items():
        article_id = existing_articles[expected_article_ix].id
        assert actual_tags.get(article_id, []) == [Tag(tag) for tag in expected_article_tags]
