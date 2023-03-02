import uuid
from asyncio import current_task

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import expression as sa_exp

from app.utils.ctx import Context


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
        self.engine: AsyncEngine = create_async_engine(
            db_uri,
        )  # db 세션 관리 방법
    
        asyncpg.Connection.prepare = _asyncpg_prepare

        self._scoped_session = async_scoped_session(
            sessionmaker(
                self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            ),
            scopefunc=lambda: Context.current.id,  # session 발급 단위 (lambda: 익명함수)
            # echo=False,  # for performance analysis
        )

    @property
    def session(self) -> AsyncSession:
        return self._scoped_session()

    async def clear_scoped_session(self) -> None:
        await self._scoped_session.remove()  # 8
