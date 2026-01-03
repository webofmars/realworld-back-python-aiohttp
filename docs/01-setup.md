# traditional python

## setup env

```sh
pyenv install
pip install poetry==1.8.2
poetry install --no-root
pip install python-dotenv
```

## run

1) be sure to have a postgres server running (cf [doc](../../README.md))
2) copy .env.default .env and customize it
3) load env vars : `source .env`
4) initialize the database structure : `poetry run alembic upgrade head`
5) start the app : `poetry run  python -m conduit`
6) validez via `curl -qSs http://127.0.0.1:5000/api/v1/articles | jq`
