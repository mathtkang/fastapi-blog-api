from boto3.session import Session
from mypy_boto3_s3.client import S3Client
import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError
from app.utils.misc import get_random_string
from app.utils.ctx import AppCtx


_executor = ThreadPoolExecutor(10)


DEFAULT_BUCKET_NAME = "fastapi-practice"

async def upload_image(
    user_id: int,
    file_name: str,
    file_obj: io.BytesIO,
) -> str:
    loop = asyncio.get_running_loop()

    random_string = get_random_string(4)
    ext_name = file_name.split(".")[-1]
    attachment_file_key = f"attachment_{user_id}_{random_string}.{ext_name}"

    try:
        await loop.run_in_executor(  
            _executor,
            AppCtx.current.s3.upload_fileobj,
            file_obj,
            DEFAULT_BUCKET_NAME,
            attachment_file_key,
            {"ContentType": f"image/{ext_name}"},
        )
    except ClientError as err:
        raise RuntimeError("AWS s3 does not response", err)

    return attachment_file_key
