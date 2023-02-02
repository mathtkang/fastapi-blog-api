from app.database.base_ import ModelBase
from app.utils.ctx import AppCtx, create_app_ctx, bind_app_ctx
from typing import AsyncIterator
from app.settings import AppSettings
import contextlib


@contextlib.asynccontextmanager
async def with_app_ctx(app_settings: AppSettings) -> AsyncIterator[AppCtx]:
    app_ctx = await create_app_ctx(app_settings)
    async with bind_app_ctx(app_ctx):
        yield app_ctx


async def ensure_fresh_env() -> None:
    async with AppCtx.current.db.engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)