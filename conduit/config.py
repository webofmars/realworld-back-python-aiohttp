__all__ = [
    "db_url",
    "settings",
]

from dynaconf import Dynaconf, Validator
from sqlalchemy import URL

settings = Dynaconf(
    envvar_prefix="CONDUIT",
    load_dotenv=True,
    validators=[
        Validator("POSTGRES_USER", required=True),
        Validator("POSTGRES_PASSWORD", required=True),
        Validator("POSTGRES_DB", required=True),
        Validator("POSTGRES_HOST", required=True),
        Validator("POSTGRES_PORT", required=True, cast=int),
        Validator("SECRET_KEY", required=True),
    ],
)
settings.validators.validate_all()


def db_url(driver: str = "postgresql+asyncpg") -> URL:
    return URL.create(
        drivername=driver,
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )
