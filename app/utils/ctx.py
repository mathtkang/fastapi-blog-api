from __future__ import annotations
import uuid
import boto3
import logging
import contextlib
from typing import TYPE_CHECKING, NamedTuple
from mypy_boto3_s3 import S3Client
from contextvars import ContextVar
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from app.settings import AppSettings
    from app.database.db import DbConn

logger = logging.getLogger(__name__)

_current_app_ctx: ContextVar[AppCtx] = ContextVar("_current_app_ctx")

class _current_app_ctx_getter:
    def __get__(self, obj, objtype=None):  # type: ignore
        return _current_app_ctx.get()


class AppCtx(NamedTuple):
    if TYPE_CHECKING:  # type: ignore
        current: AppCtx

    settings: AppSettings
    db: DbConn
    s3: S3Client

    id: str | None = None


async def create_app_ctx(app_settings: AppSettings) -> AppCtx:
    from app.database.db import DbConn

    return AppCtx(
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
async def bind_app_ctx(app_ctx: AppCtx) -> AsyncIterator[None]:
    ctx_token = _current_app_ctx.set(app_ctx._replace(id=str(uuid.uuid4())))  # 4
    try:
        yield  # 5
    finally:
        try:
            await app_ctx.db.clear_scoped_session()  # 7
        except Exception:
            logger.warning("Failed to clear scoped session", exc_info=True)

        _current_app_ctx.reset(ctx_token)  # 9


AppCtx.current = _current_app_ctx_getter()  # type: ignore
