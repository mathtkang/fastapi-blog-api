import contextlib
from typing import AsyncIterator

from app.database.base_ import ModelBase
from app.settings import AppSettings
from app.utils.ctx import Context, bind_context, create_app_ctx


@contextlib.asynccontextmanager
async def with_app_ctx(app_settings: AppSettings) -> AsyncIterator[Context]:
    app_ctx = await create_app_ctx(app_settings)
    async with bind_context(app_ctx):
        yield app_ctx


async def ensure_fresh_env() -> None:
    async with Context.current.db.engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)
