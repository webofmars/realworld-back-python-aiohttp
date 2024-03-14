FROM python:3.11-bookworm AS builder

ENV POETRY_HOME=/opt/poetry
RUN python -m venv $POETRY_HOME && $POETRY_HOME/bin/pip install poetry==1.8.2

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock


FROM builder AS migrations

WORKDIR /opt/conduit_migrations

RUN $POETRY_HOME/bin/poetry config virtualenvs.create false && \
    $POETRY_HOME/bin/poetry install --only migrations --no-root

COPY conduit conduit
COPY migrations migrations
ENTRYPOINT ["alembic"]
CMD ["upgrade", "head"]


FROM builder AS runtime

WORKDIR /opt/conduit

RUN $POETRY_HOME/bin/poetry config virtualenvs.create false && \
    $POETRY_HOME/bin/poetry install --only main --no-root

COPY conduit conduit
CMD ["python", "-m", "conduit"]
