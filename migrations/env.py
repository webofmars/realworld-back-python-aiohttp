import os
import typing as t
from logging.config import fileConfig

from alembic import context
from alembic.operations import MigrationScript
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import URL, create_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_env(name: str, default: str | None = None) -> str:
    env = os.getenv(name, default)
    if env is None:
        raise ValueError(f"env variable ({name}) must be set")
    return env


def process_revision_directives(
    context: MigrationContext,
    revision: str | t.Iterable[str | None] | t.Iterable[str],
    directives: list[MigrationScript],
) -> None:
    if context.config is None:
        raise ValueError("migration environment config must be defined")
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()
    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision.lstrip("0"))
        new_rev_id = last_rev_id + 1
    migration_script.rev_id = f"{new_rev_id:04}"


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        url=URL.create(
            drivername="postgresql+psycopg2",
            username=get_env("POSTGRES_USER"),
            password=get_env("POSTGRES_PASSWORD"),
            database=get_env("POSTGRES_DB"),
            host=get_env("POSTGRES_HOST"),
            port=int(get_env("POSTGRES_PORT")),
        )
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
