from typing import TYPE_CHECKING, NamedTuple
from mypy_boto3_s3 import S3Client


if TYPE_CHECKING:
    from app.settings import AppSettings
    from app.database.db import engine


class AppCtx(NamedTuple):
    # if TYPE_CHECKING:  # type: ignore
    #     current: AppCtx  # question

    app_settings: AppSettings
    # settings: AppSettings
    db: engine
    s3: S3Client

    id: str | None = None