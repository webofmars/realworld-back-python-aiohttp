__all__ = [
    "Dependencies",
    "UseCases",
    "create_app",
]

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import DependenciesContainer, Provider, Singleton
from sqlalchemy.ext.asyncio import create_async_engine

from conduit.api.errors import error_handling_middleware
from conduit.api.profiles.follow import follow_endpoint
from conduit.api.profiles.get import get_profile_endpoint
from conduit.api.profiles.unfollow import unfollow_endpoint
from conduit.api.users import (
    get_current_user_endpoint,
    sign_in_endpoint,
    sign_up_endpoint,
    update_current_user_endpoint,
)
from conduit.config import db_url, settings
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.auth import WithAuthentication
from conduit.core.use_cases.profiles.follow import FollowInput, FollowResult, FollowUseCase
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileResult, GetProfileUseCase
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowResult, UnfollowUseCase
from conduit.core.use_cases.users.get_current import GetCurrentUserInput, GetCurrentUserResult, GetCurrentUserUseCase
from conduit.core.use_cases.users.sign_in import SignInInput, SignInResult, SignInUseCase
from conduit.core.use_cases.users.sign_up import SignUpInput, SignUpResult, SignUpUseCase
from conduit.core.use_cases.users.update_current import (
    UpdateCurrentUserInput,
    UpdateCurrentUserResult,
    UpdateCurrentUserUseCase,
)
from conduit.impl.auth_token_generator import JwtAuthTokenGenerator
from conduit.impl.password_hasher import Argon2idPasswordHasher
from conduit.impl.unit_of_work import PostgresqlUnitOfWork


def create_app() -> web.Application:
    use_cases = UseCases(deps=Dependencies())
    use_cases.check_dependencies()

    app = web.Application()
    app.add_routes(
        [
            # Users
            web.post("/api/v1/users", sign_up_endpoint(use_cases.sign_up())),
            web.post("/api/v1/users/login", sign_in_endpoint(use_cases.sign_in())),
            web.get("/api/v1/user", get_current_user_endpoint(use_cases.get_current_user())),
            web.put("/api/v1/user", update_current_user_endpoint(use_cases.update_current_user())),
            # Profiles
            web.get("/api/v1/profiles/{username}", get_profile_endpoint(use_cases.get_profile())),
            web.post("/api/v1/profiles/{username}/follow", follow_endpoint(use_cases.follow())),
            web.delete("/api/v1/profiles/{username}/follow", unfollow_endpoint(use_cases.unfollow())),
        ]
    )
    app.middlewares.append(validation_middleware)
    app.middlewares.append(error_handling_middleware)

    setup_aiohttp_apispec(
        app=app,
        title="Conduit API",
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )
    return app


class Dependencies(DeclarativeContainer):
    """Application's dependencies."""

    db = Singleton(create_async_engine, db_url())
    unit_of_work = Singleton(PostgresqlUnitOfWork, db)
    password_hasher = Singleton(Argon2idPasswordHasher)
    auth_token_generator = Singleton(JwtAuthTokenGenerator, secret_key=settings.SECRET_KEY)


class UseCases(DeclarativeContainer):
    """Application's use cases."""

    deps = DependenciesContainer()

    # Users
    sign_up: Provider[UseCase[SignUpInput, SignUpResult]] = Singleton(
        SignUpUseCase,
        unit_of_work=deps.unit_of_work,
        password_hasher=deps.password_hasher,
        auth_token_generator=deps.auth_token_generator,
    )
    sign_in: Provider[UseCase[SignInInput, SignInResult]] = Singleton(
        SignInUseCase,
        unit_of_work=deps.unit_of_work,
        password_hasher=deps.password_hasher,
        auth_token_generator=deps.auth_token_generator,
    )
    get_current_user: Provider[UseCase[GetCurrentUserInput, GetCurrentUserResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(GetCurrentUserUseCase, unit_of_work=deps.unit_of_work),
    )
    update_current_user: Provider[UseCase[UpdateCurrentUserInput, UpdateCurrentUserResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(
            UpdateCurrentUserUseCase,
            unit_of_work=deps.unit_of_work,
            password_hasher=deps.password_hasher,
        ),
    )

    # Profiles
    get_profile: Provider[UseCase[GetProfileInput, GetProfileResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(GetProfileUseCase, unit_of_work=deps.unit_of_work),
    )
    follow: Provider[UseCase[FollowInput, FollowResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(FollowUseCase, unit_of_work=deps.unit_of_work),
    )
    unfollow: Provider[UseCase[UnfollowInput, UnfollowResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(UnfollowUseCase, unit_of_work=deps.unit_of_work),
    )
