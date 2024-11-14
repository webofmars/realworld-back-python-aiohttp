# traditional python

## setup env

```sh
virtualenv -p $(which python3.11) .venv
source .venv/bin/activate
pip install -U pip
pip install poetry==1.8.2
poetry install --no-root
pip install python-dotenv
```

## run

1) be sure to have a postgres server running (cf [doc](../../README.md))
2) copy .env.default .env and customize it
3) load env vars : `source .env`
4) initialize the database structure : `alembic upgrade head`
5) start the app : `python -m conduit`
