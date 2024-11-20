FROM python:3.11-bookworm AS builder

ENV POETRY_HOME=/opt/poetry
RUN python -m venv $POETRY_HOME && $POETRY_HOME/bin/pip install poetry==1.8.2

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

FROM builder AS runtime

WORKDIR /opt/conduit

RUN --mount=type=cache,target=/root/.cache/pip \
    $POETRY_HOME/bin/poetry config virtualenvs.create false && \
    $POETRY_HOME/bin/poetry install --no-root

COPY migrations migrations
COPY conduit conduit
CMD ["python", "-m", "conduit"]
