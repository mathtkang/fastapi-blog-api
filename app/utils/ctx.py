from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from mypy_boto3_s3 import S3Client
from contextvars import ContextVar

if TYPE_CHECKING:
    from app.settings import AppSettings
    from app.database.db import DbConn




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

AppCtx.current = _current_app_ctx_getter()  # type: ignore