from asyncio import current_task
from sqlalchemy import create_engine
from sqlalchemy.sql import expression as sa_exp
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from app.settings import AppSettings

app_settings = AppSettings()

engine = create_async_engine(app_settings.DATABASE_URL)  
# async_session_factory = sessionmaker(bind=engine, class_=AsyncSession)
# session = async_scoped_session(
#     session_factory=async_session_factory,
#     scopefunc=current_task,
# )




async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
