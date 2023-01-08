from fastapi import Depends, APIRouter, HTTPException, UploadFile
from db.db import get_session
from utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import models as m
from sqlalchemy.sql import expression as sql_exp
from utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
import jwt, time
from mypy_boto3_s3.client import S3Client
from utils.blob import get_blob_client
from utils.misc import get_random_string


router = APIRouter(prefix="/attachment", tags=["attachment"])


class PostAttachmentResponse(BaseModel):
    bucket: str
    key: str


@router.post("")
def post_attachment(
    file: UploadFile,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
    blob_client: S3Client = Depends(get_blob_client),
):
    """
    파일스토리지
    1. session
    2. resolve access token (user_id)
    3. blob client
    4. 사용자의 입력(file)
    """
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )
    random_string = get_random_string(4)
    ext_name = file.filename.split(".")[-1]
    attachment_file_key = f"attachment_{user_id}_{random_string}.{ext_name}"

    blob_client.upload_fileobj(file.file, "fastapi-practice", attachment_file_key)

    return PostAttachmentResponse(bucket="fastapi-practice", key=attachment_file_key)


# URL: 제한시간, 해당 리소스에만 접근 가능

# 1. upload file by this endpoint
# 2. get the attachment file key
# 3. upload attachment key to post or user
# 4. get attachment file url by user get endpoint or post get endpoint
