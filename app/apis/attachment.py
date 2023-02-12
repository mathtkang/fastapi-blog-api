from fastapi import Depends, APIRouter, HTTPException, UploadFile
from app.utils.auth import resolve_access_token
from sqlalchemy.ext.asyncio import AsyncSession as Session
from pydantic import BaseModel
from app.database import models as m
from sqlalchemy.sql import expression as sql_exp
from app.utils.blob import upload_image
from starlette.status import HTTP_403_FORBIDDEN
from mypy_boto3_s3.client import S3Client
from app.utils.ctx import AppCtx


router = APIRouter(prefix="/attachment", tags=["attachment"])


class PostAttachmentResponse(BaseModel):
    bucket: str
    key: str


@router.post("")
async def post_attachment(
    file: UploadFile,
    user_id: int = Depends(resolve_access_token),
):
    """
    파일스토리지
    1. session
    2. resolve access token (user_id)
    3. blob client
    4. 사용자의 입력(file)
    """
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    attachment_file_key = await upload_image(
        user_id, 
        file.filee, 
        file.file
    )

    return PostAttachmentResponse(bucket="fastapi-practice", key=attachment_file_key)


# 유저 profile_file 가져오기







# URL: 제한시간, 해당 리소스에만 접근 가능

# 1. upload file by this endpoint
# 2. get the attachment file key
# 3. upload attachment key to post or user
# 4. get attachment file url by user get endpoint or post get endpoint