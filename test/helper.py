from app.database.base_ import ModelBase
from app.utils.ctx import AppCtx


async def ensure_fresh_env() -> None:
    async with AppCtx.current.db.engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)
    await AppCtx.current.db.flushall()   # question