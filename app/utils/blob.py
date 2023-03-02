import asyncio
import io
from concurrent.futures import ThreadPoolExecutor

from botocore.exceptions import ClientError

from app.utils.ctx import Context
from app.utils.misc import get_random_string

_executor = ThreadPoolExecutor(10)


DEFAULT_BUCKET_NAME = "fastapi-practice"
A_ONE_DAY = 60 * 60 * 24


async def upload_profile_img(
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
            Context.current.s3.upload_fileobj,
            file_obj,
            DEFAULT_BUCKET_NAME,
            attachment_file_key,
            {"ContentType": f"image/{ext_name}"},
        )
    except ClientError as err:
        raise RuntimeError("AWS s3 does not response", err)

    return attachment_file_key


# TRY, ERROR
# async def get_image_url(
#     attachment_file_key,
# ) -> str:
#     loop = asyncio.get_running_loop()
    
#     return await loop.run_in_executor(
#         _executor,
#         AppCtx.current.s3.generate_presigned_url,
#         "get_object",
#         Params={
#             "Bucket": DEFAULT_BUCKET_NAME,  # 서버에서 버킷 안 보냄(db의 테이블과 같은 의미)
#             "Key": attachment_file_key,  # key는 유저에 따라서 바뀔 수 있음
#         },
#         ExpiresIn=A_ONE_DAY,
#     )


# DONE
def get_image_url(
    attachment_file_key,
) -> str:
    return Context.current.s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": DEFAULT_BUCKET_NAME,  # 서버에서 버킷 안 보냄(db의 테이블과 같은 의미)
            "Key": attachment_file_key,  # key는 유저에 따라서 바뀔 수 있음
        },
        ExpiresIn=A_ONE_DAY,
    )