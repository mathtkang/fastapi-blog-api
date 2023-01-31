import uuid
import asyncpg
from asyncio import current_task
from sqlalchemy import create_engine
from sqlalchemy.sql import expression as sa_exp
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from sqlalchemy.orm import sessionmaker

from app.utils.ctx import AppCtx


# [before]
# app_settings = AppSettings()

# engine = create_async_engine(app_settings.DATABASE_URL)  

# async def get_session() -> AsyncSession:
#     async with AsyncSession(engine) as session:
#         yield session



# [after]
async def _asyncpg_prepare(  # type: ignore
    self,
    query,
    *,
    name=None,
    timeout=None,
    record_class=None,
):
    return await self._prepare(
        query,
        name=str(uuid.uuid1()) if name is None else name,  # hotfix
        timeout=timeout,
        use_cache=False,
        record_class=record_class,
    )

class DbConn:
    def __init__(self, db_uri: str) -> None:
        self.engine: AsyncEngine = create_async_engine(db_uri)
    
        asyncpg.Connection.prepare = _asyncpg_prepare

        self._scoped_session = async_scoped_session(
            sessionmaker(
                self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            ),
            scopefunc=lambda: AppCtx.current.id,
        )
    
    @property
    def session(self) -> AsyncSession:
        return self._scoped_session()

    async def clear_scoped_session(self) -> None:
        await self._scoped_session.remove()
