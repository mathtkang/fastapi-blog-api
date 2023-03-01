from __future__ import annotations

import contextlib
import logging
import uuid
from contextvars import ContextVar
from typing import TYPE_CHECKING, AsyncIterator, NamedTuple

import boto3
from mypy_boto3_s3 import S3Client

if TYPE_CHECKING:
    from app.database.db import DbConn
    from app.settings import AppSettings

logger = logging.getLogger(__name__)

_current_context: ContextVar[Context] = ContextVar("_current_context")

class _current_context_getter:
    def __get__(self, obj, objtype=None):  # type: ignore
        return _current_context.get()


class Context(NamedTuple):
    if TYPE_CHECKING:  # type: ignore
        current: Context

    settings: AppSettings
    db: DbConn
    s3: S3Client

    id: str | None = None


async def create_app_ctx(app_settings: AppSettings) -> Context:
    from app.database.db import DbConn

    return Context(
        settings=app_settings,
        db=DbConn(app_settings.DATABASE_URL),
        s3=boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id=app_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=app_settings.AWS_SECRET_ACCESS_KEY,
        ),
    )


@contextlib.asynccontextmanager
async def bind_app_ctx(app_ctx: Context) -> AsyncIterator[None]:
    ctx_token = _current_context.set(app_ctx._replace(id=str(uuid.uuid4())))  # 4
    try:
        yield  # 5
    finally:
        try:
            await app_ctx.db.clear_scoped_session()  # 7
        except Exception:
            logger.warning("Failed to clear scoped session", exc_info=True)

        _current_context.reset(ctx_token)  # 9


Context.current = _current_context_getter()  # type: ignore
