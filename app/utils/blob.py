from boto3.session import Session
from mypy_boto3_s3.client import S3Client
import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError
from utils.misc import get_random_string


_executor = ThreadPoolExecutor(10)

def get_blob_client() -> S3Client:
    return Session().client("s3")


DEFAULT_BUCKET_NAME = "fastapi-practice"

async def upload_image(
    blob_client: S3Client,
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
            blob_client.upload_fileobj,  # sync
            file_obj,
            DEFAULT_BUCKET_NAME,
            attachment_file_key,
            {"ContentType": f"image/{ext_name}"},
        )
    except ClientError as err:
        raise RuntimeError("AWS s3 does not response", err)

    return attachment_file_key
