from fastapi import FastAPI, Request, Response
from .settings import AppSettings
from .apis import API_ROUTERS
import functools
from app.utils.ctx import AppCtx, create_app_ctx, bind_app_ctx
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger(__name__)


def create_app(app_settings: AppSettings) -> FastAPI:
    # 앱 함수 실행
    app = FastAPI()

    app.add_event_handler(
        "startup", functools.partial(_web_app_startup, app, app_settings)
    )
    app.add_event_handler("shutdown", functools.partial(_web_app_shutdown, app))

    # 라우터 정의
    for api_router in API_ROUTERS:
        app.include_router(api_router)

    return app


async def _web_app_startup(app: FastAPI, app_settings: AppSettings) -> None:
    app_ctx = await create_app_ctx(app_settings)

    app.extra["_app_ctx"] = app_ctx

    if app_settings.DEBUG_ALLOW_CORS_ALL_ORIGIN:
        app.add_middleware(
            CORSMiddleware,  # 1
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.error("`DEBUG_ALLOW_CORS_ALL_ORIGIN` is on!")

    async def _ctx_middleware(
        request: Request, call_next: RequestResponseEndpoint  
    ) -> Response:
        async with bind_app_ctx(app_ctx):  # 3
            response = await call_next(request)  # 6
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_ctx_middleware)  # 2


async def _web_app_shutdown(app: FastAPI) -> None:
    app_ctx: AppCtx = app.extra["_app_ctx"]

    try:
        await app_ctx.db.engine.dispose()
    except Exception:
        logger.warning("Failed dispose DB engine", exc_info=True)