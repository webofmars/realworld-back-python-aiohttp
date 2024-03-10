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

from conduit.api.articles.create import create_article_endpoint
from conduit.api.articles.delete import delete_article_endpoint
from conduit.api.articles.favorite import favorite_article_endpoint
from conduit.api.articles.feed import feed_articles_endpoint
from conduit.api.articles.get import get_article_endpoint
from conduit.api.articles.list import list_articles_endpoint
from conduit.api.articles.unfavorite import unfavorite_article_endpoint
from conduit.api.articles.update import update_article_endpoint
from conduit.api.comments.add_to_article import add_comment_to_article_endpoint
from conduit.api.comments.delete import delete_comment_endpoint
from conduit.api.comments.get_from_article import get_comments_from_article_endpoint
from conduit.api.errors import domain_error_handling_middleware
from conduit.api.middlewares import logging_middleware, request_id_middleware
from conduit.api.profiles.follow import follow_endpoint
from conduit.api.profiles.get import get_profile_endpoint
from conduit.api.profiles.unfollow import unfollow_endpoint
from conduit.api.tags.list import list_tags_endpoint
from conduit.api.users import (
    get_current_user_endpoint,
    sign_in_endpoint,
    sign_up_endpoint,
    update_current_user_endpoint,
)
from conduit.config import db_url, settings
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.articles.create import CreateArticleInput, CreateArticleResult, CreateArticleUseCase
from conduit.core.use_cases.articles.delete import DeleteArticleInput, DeleteArticleResult, DeleteArticleUseCase
from conduit.core.use_cases.articles.favorite import FavoriteArticleInput, FavoriteArticleResult, FavoriteArticleUseCase
from conduit.core.use_cases.articles.feed import FeedArticlesInput, FeedArticlesResult, FeedArticlesUseCase
from conduit.core.use_cases.articles.get import GetArticleInput, GetArticleResult, GetArticleUseCase
from conduit.core.use_cases.articles.list import ListArticlesInput, ListArticlesResult, ListArticlesUseCase
from conduit.core.use_cases.articles.unfavorite import (
    UnfavoriteArticleInput,
    UnfavoriteArticleResult,
    UnfavoriteArticleUseCase,
)
from conduit.core.use_cases.articles.update import UpdateArticleInput, UpdateArticleResult, UpdateArticleUseCase
from conduit.core.use_cases.auth import WithAuthentication
from conduit.core.use_cases.comments.add_to_article import (
    AddCommentToArticleInput,
    AddCommentToArticleResult,
    AddCommentToArticleUseCase,
)
from conduit.core.use_cases.comments.delete import DeleteCommentInput, DeleteCommentResult, DeleteCommentUseCase
from conduit.core.use_cases.comments.get_from_article import (
    GetCommentsFromArticleInput,
    GetCommentsFromArticleResult,
    GetCommentsFromArticleUseCase,
)
from conduit.core.use_cases.profiles.follow import FollowInput, FollowResult, FollowUseCase
from conduit.core.use_cases.profiles.get import GetProfileInput, GetProfileResult, GetProfileUseCase
from conduit.core.use_cases.profiles.unfollow import UnfollowInput, UnfollowResult, UnfollowUseCase
from conduit.core.use_cases.tags.list import ListTagsInput, ListTagsResult, ListTagsUseCase
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
            # Articles
            web.post("/api/v1/articles", create_article_endpoint(use_cases.create_article())),
            web.get("/api/v1/articles", list_articles_endpoint(use_cases.list_articles())),
            web.get("/api/v1/articles/feed", feed_articles_endpoint(use_cases.feed_articles())),
            web.get("/api/v1/articles/{slug}", get_article_endpoint(use_cases.get_article())),
            web.put("/api/v1/articles/{slug}", update_article_endpoint(use_cases.update_article())),
            web.delete("/api/v1/articles/{slug}", delete_article_endpoint(use_cases.delete_article())),
            web.post("/api/v1/articles/{slug}/favorite", favorite_article_endpoint(use_cases.favorite_article())),
            web.delete("/api/v1/articles/{slug}/favorite", unfavorite_article_endpoint(use_cases.unfavorite_article())),
            # Comments
            web.post(
                "/api/v1/articles/{slug}/comments",
                add_comment_to_article_endpoint(use_cases.add_comment_to_article()),
            ),
            web.get(
                "/api/v1/articles/{slug}/comments",
                get_comments_from_article_endpoint(use_cases.get_comments_from_article()),
            ),
            web.delete(
                r"/api/v1/articles/{slug}/comments/{comment_id:\d+}",
                delete_comment_endpoint(use_cases.delete_comment()),
            ),
            # Tags
            web.get("/api/v1/tags", list_tags_endpoint(use_cases.list_tags())),
        ]
    )
    app.middlewares.extend(
        [
            request_id_middleware,
            logging_middleware,
            validation_middleware,
            domain_error_handling_middleware,
        ]
    )

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

    # Articles
    create_article: Provider[UseCase[CreateArticleInput, CreateArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(CreateArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    list_articles: Provider[UseCase[ListArticlesInput, ListArticlesResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(ListArticlesUseCase, unit_of_work=deps.unit_of_work),
    )
    feed_articles: Provider[UseCase[FeedArticlesInput, FeedArticlesResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(FeedArticlesUseCase, unit_of_work=deps.unit_of_work),
    )
    get_article: Provider[UseCase[GetArticleInput, GetArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(GetArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    update_article: Provider[UseCase[UpdateArticleInput, UpdateArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(UpdateArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    delete_article: Provider[UseCase[DeleteArticleInput, DeleteArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(DeleteArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    favorite_article: Provider[UseCase[FavoriteArticleInput, FavoriteArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(FavoriteArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    unfavorite_article: Provider[UseCase[UnfavoriteArticleInput, UnfavoriteArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(UnfavoriteArticleUseCase, unit_of_work=deps.unit_of_work),
    )

    # Comments
    add_comment_to_article: Provider[UseCase[AddCommentToArticleInput, AddCommentToArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(AddCommentToArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    get_comments_from_article: Provider[UseCase[GetCommentsFromArticleInput, GetCommentsFromArticleResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(GetCommentsFromArticleUseCase, unit_of_work=deps.unit_of_work),
    )
    delete_comment: Provider[UseCase[DeleteCommentInput, DeleteCommentResult]] = Singleton(
        WithAuthentication,
        auth_token_generator=deps.auth_token_generator,
        use_case=Singleton(DeleteCommentUseCase, unit_of_work=deps.unit_of_work),
    )

    # Tags
    list_tags: Provider[UseCase[ListTagsInput, ListTagsResult]] = Singleton(
        ListTagsUseCase,
        unit_of_work=deps.unit_of_work,
    )
